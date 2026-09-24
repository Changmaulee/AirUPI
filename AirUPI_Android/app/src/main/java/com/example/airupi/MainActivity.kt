package com.example.airupi

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothServerSocket
import android.bluetooth.BluetoothSocket
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.hardware.camera2.CameraManager
import android.hardware.usb.UsbAccessory
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.ParcelFileDescriptor
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.view.ViewGroup
import android.webkit.JavascriptInterface
import android.webkit.PermissionRequest
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import java.io.BufferedReader
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.io.FileWriter
import java.io.InputStreamReader
import java.io.OutputStream
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.HttpURLConnection
import java.net.Inet4Address
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.NetworkInterface
import java.net.ServerSocket
import java.net.Socket
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID
import java.util.concurrent.Executors

class MainActivity : ComponentActivity(), TextToSpeech.OnInitListener, SensorEventListener {

    private var tts: TextToSpeech? = null
    private var webView: WebView? = null
    private var serverSocket: ServerSocket? = null
    private var usbVaultServerSocket: ServerSocket? = null
    private var udpSocket: DatagramSocket? = null
    private var bluetoothServerSocket: BluetoothServerSocket? = null
    private var usbManager: UsbManager? = null
    private var sensorManager: SensorManager? = null
    private var magneticSensor: Sensor? = null
    private var accelSensor: Sensor? = null
    private var lightSensor: Sensor? = null
    private var vibrator: Vibrator? = null
    private var cameraManager: CameraManager? = null
    private var mainCameraId: String? = null

    private var currentMag = 45.0
    private var currentAccel = 9.8
    private var currentLux = 120.0
    private var lastTriggerTime = 0L
    private var lastTelemetryDispatch = 0L

    private var isUsbConnected = false
    private var isMeshRunning = false
    private val executor = Executors.newCachedThreadPool()

    private val AIR_UPI_BT_UUID: UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")

    private val usbReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val action = intent?.action
            if (action == UsbManager.ACTION_USB_DEVICE_ATTACHED ||
                action == UsbManager.ACTION_USB_ACCESSORY_ATTACHED ||
                action == "android.hardware.usb.action.USB_STATE"
            ) {
                val extrasConnected = intent.extras?.getBoolean("connected", false) ?: false
                val hasDevices = (usbManager?.deviceList?.isNotEmpty() == true) || (usbManager?.accessoryList?.isNotEmpty() == true)
                isUsbConnected = extrasConnected || hasDevices
                notifyUsbStateToWeb(isUsbConnected)
            } else if (action == UsbManager.ACTION_USB_DEVICE_DETACHED || action == UsbManager.ACTION_USB_ACCESSORY_DETACHED) {
                isUsbConnected = false
                notifyUsbStateToWeb(false)
            }
        }
    }

    private fun notifyUsbStateToWeb(connected: Boolean) {
        runOnUiThread {
            webView?.evaluateJavascript("if (window.onUsbStateChanged) window.onUsbStateChanged($connected);", null)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        tts = TextToSpeech(this, this)
        tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {}
            override fun onDone(utteranceId: String?) {
                runOnUiThread {
                    webView?.evaluateJavascript("if (window.onTtsFinished) window.onTtsFinished();", null)
                }
            }
            @Deprecated("Deprecated in Java")
            override fun onError(utteranceId: String?) {
                runOnUiThread {
                    webView?.evaluateJavascript("if (window.onTtsFinished) window.onTtsFinished();", null)
                }
            }
        })

        val permissions = mutableListOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.MODIFY_AUDIO_SETTINGS,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            permissions.add(Manifest.permission.BLUETOOTH_CONNECT)
            permissions.add(Manifest.permission.BLUETOOTH_SCAN)
            permissions.add(Manifest.permission.BLUETOOTH_ADVERTISE)
        }

        val missing = permissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missing.toTypedArray(), 101)
        }

        usbManager = getSystemService(Context.USB_SERVICE) as? UsbManager
        try {
            val filter = IntentFilter().apply {
                addAction(UsbManager.ACTION_USB_DEVICE_ATTACHED)
                addAction(UsbManager.ACTION_USB_DEVICE_DETACHED)
                addAction(UsbManager.ACTION_USB_ACCESSORY_ATTACHED)
                addAction(UsbManager.ACTION_USB_ACCESSORY_DETACHED)
                addAction("android.hardware.usb.action.USB_STATE")
            }
            registerReceiver(usbReceiver, filter)
            isUsbConnected = (usbManager?.deviceList?.isNotEmpty() == true) || (usbManager?.accessoryList?.isNotEmpty() == true)
        } catch (_: Exception) {}

        // Initialize Sensors & Actuators
        sensorManager = getSystemService(Context.SENSOR_SERVICE) as? SensorManager
        magneticSensor = sensorManager?.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD)
        accelSensor = sensorManager?.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        lightSensor = sensorManager?.getDefaultSensor(Sensor.TYPE_LIGHT)

        vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val vibratorManager = getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager
            vibratorManager?.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
        }

        cameraManager = getSystemService(Context.CAMERA_SERVICE) as? CameraManager
        try {
            mainCameraId = cameraManager?.cameraIdList?.firstOrNull { id ->
                val chars = cameraManager?.getCameraCharacteristics(id)
                chars?.get(android.hardware.camera2.CameraCharacteristics.FLASH_INFO_AVAILABLE) == true
            }
        } catch (_: Exception) {}

        // Register default sensor telemetry listeners
        sensorManager?.let { sm ->
            magneticSensor?.let { sm.registerListener(this@MainActivity, it, SensorManager.SENSOR_DELAY_UI) }
            accelSensor?.let { sm.registerListener(this@MainActivity, it, SensorManager.SENSOR_DELAY_UI) }
            lightSensor?.let { sm.registerListener(this@MainActivity, it, SensorManager.SENSOR_DELAY_UI) }
        }

        startZeroCloudMesh()

        setContent {
            AndroidView(
                modifier = Modifier.fillMaxSize(),
                factory = { context ->
                    WebView(context).apply {
                        webView = this
                        layoutParams = ViewGroup.LayoutParams(
                            ViewGroup.LayoutParams.MATCH_PARENT,
                            ViewGroup.LayoutParams.MATCH_PARENT
                        )
                        
                        settings.apply {
                            javaScriptEnabled = true
                            domStorageEnabled = true
                            allowFileAccess = true
                            allowContentAccess = true
                            mediaPlaybackRequiresUserGesture = false
                            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
                            useWideViewPort = true
                            loadWithOverviewMode = true
                        }

                        addJavascriptInterface(SoundboxBridge(), "AirUPIAndroid")

                        webViewClient = object : WebViewClient() {}

                        webChromeClient = object : WebChromeClient() {
                            override fun onPermissionRequest(request: PermissionRequest?) {
                                runOnUiThread {
                                    request?.grant(request.resources)
                                }
                            }
                        }

                        loadUrl("file:///android_asset/index.html")
                    }
                }
            )
        }
    }

    private fun startZeroCloudMesh() {
        if (isMeshRunning) return
        isMeshRunning = true

        // 1. Local HTTP / File-Drop Server on Port 8080
        executor.execute {
            try {
                serverSocket = ServerSocket(8080)
                while (isMeshRunning && !serverSocket!!.isClosed) {
                    val client = serverSocket!!.accept()
                    handleHttpClient(client)
                }
            } catch (_: Exception) {}
        }

        // 2. Subnet UDP Broadcast Listener on Port 8088
        executor.execute {
            try {
                udpSocket = DatagramSocket(8088)
                udpSocket?.broadcast = true
                val buffer = ByteArray(1024)
                while (isMeshRunning && !udpSocket!!.isClosed) {
                    val packet = DatagramPacket(buffer, buffer.size)
                    udpSocket?.receive(packet)
                    val msg = String(packet.data, 0, packet.length).trim()
                    processRawPacket(msg, "Wi-Fi Broadcast")
                }
            } catch (_: Exception) {}
        }

        // 3. Bluetooth RFCOMM Server for Airplane Mode
        executor.execute {
            try {
                val btManager = getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
                val btAdapter = btManager?.adapter ?: BluetoothAdapter.getDefaultAdapter()
                if (btAdapter != null && btAdapter.isEnabled) {
                    bluetoothServerSocket = btAdapter.listenUsingRfcommWithServiceRecord("AirUPISoundbox", AIR_UPI_BT_UUID)
                    while (isMeshRunning && bluetoothServerSocket != null) {
                        val btSocket = bluetoothServerSocket?.accept()
                        if (btSocket != null) {
                            handleBluetoothClient(btSocket)
                        }
                    }
                }
            } catch (_: Exception) {}
        }

        // 4. Type-C Hardwired Vault Direct Socket on Port 8089
        executor.execute {
            try {
                usbVaultServerSocket = ServerSocket(8089)
                while (isMeshRunning && !usbVaultServerSocket!!.isClosed) {
                    val client = usbVaultServerSocket!!.accept()
                    executor.execute {
                        try {
                            val reader = BufferedReader(InputStreamReader(client.getInputStream()))
                            val line = reader.readLine()
                            if (line != null) {
                                processRawPacket(line, "Type-C Hardwired Vault")
                                val out = client.getOutputStream()
                                out.write("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{\"status\":\"COMMITTED_OVER_TYPE_C\"}\r\n".toByteArray())
                                out.flush()
                            }
                            client.close()
                        } catch (_: Exception) {
                            try { client.close() } catch (_: Exception) {}
                        }
                    }
                }
            } catch (_: Exception) {}
        }
    }

    private fun handleBluetoothClient(socket: BluetoothSocket) {
        executor.execute {
            try {
                val reader = BufferedReader(InputStreamReader(socket.inputStream))
                val line = reader.readLine()
                if (line != null) {
                    processRawPacket(line, "Bluetooth Radio")
                }
                socket.close()
            } catch (_: Exception) {
                try { socket.close() } catch (_: Exception) {}
            }
        }
    }

    private fun processRawPacket(msg: String, source: String) {
        if (msg.startsWith("AIR_PAY:")) {
            var amt = 1
            var lang = "hi"
            var tx = "AIR_RADIO_" + (System.currentTimeMillis() % 10000)
            var token = ""

            val parts = msg.split(":")
            for (part in parts) {
                val kv = part.split("=")
                if (kv.size == 2) {
                    when (kv[0]) {
                        "amt" -> amt = kv[1].toIntOrNull() ?: 1
                        "lang" -> lang = kv[1]
                        "tx" -> tx = kv[1]
                        "token" -> token = kv[1]
                    }
                }
            }

            appendLocalLedgerFile(amt, lang, tx, token, source)

            runOnUiThread {
                val js = "if (window.handleIncomingPayment) { window.handleIncomingPayment({ amount: $amt, lang: '$lang', tx: '$tx', token: '$token', source: '$source' }); }"
                webView?.evaluateJavascript(js, null)
            }
        }
    }

    private fun handleHttpClient(socket: Socket) {
        executor.execute {
            try {
                val reader = BufferedReader(InputStreamReader(socket.getInputStream()))
                val line = reader.readLine() ?: return@execute
                
                val parts = line.split(" ")
                if (parts.size >= 2) {
                    val path = parts[1]
                    
                    // Route 1: Download Daily Ledger CSV
                    if (path.startsWith("/ledger.csv") || path.startsWith("/export")) {
                        val csvContent = getLedgerCsvContent()
                        val out: OutputStream = socket.getOutputStream()
                        val response = "HTTP/1.1 200 OK\r\n" +
                                "Content-Type: text/csv\r\n" +
                                "Content-Disposition: attachment; filename=\"AirUPI_Daily_Ledger.csv\"\r\n" +
                                "Access-Control-Allow-Origin: *\r\n" +
                                "Content-Length: ${csvContent.toByteArray().size}\r\n" +
                                "Connection: close\r\n\r\n" +
                                csvContent
                        out.write(response.toByteArray())
                        out.flush()
                    }
                    // Route 2: Direct File-Drop Payment Receipt (POST /drop or GET /pay)
                    else if (path.startsWith("/pay") || path.startsWith("/drop")) {
                        var amt = 1
                        var lang = "hi"
                        var tx = "AIR_HTTP_" + (System.currentTimeMillis() % 10000)
                        var token = ""

                        val queryIndex = path.indexOf('?')
                        if (queryIndex != -1) {
                            val queryString = path.substring(queryIndex + 1)
                            for (param in queryString.split("&")) {
                                val kv = param.split("=")
                                if (kv.size == 2) {
                                    when (kv[0]) {
                                        "amt" -> amt = kv[1].toIntOrNull() ?: 1
                                        "lang" -> lang = kv[1]
                                        "tx" -> tx = kv[1]
                                        "token" -> token = kv[1]
                                    }
                                }
                            }
                        }

                        appendLocalLedgerFile(amt, lang, tx, token, "HTTP File-Drop")

                        runOnUiThread {
                            val js = "if (window.handleIncomingPayment) { window.handleIncomingPayment({ amount: $amt, lang: '$lang', tx: '$tx', token: '$token', source: 'HTTP File-Drop' }); }"
                            webView?.evaluateJavascript(js, null)
                        }

                        val responseBody = "{\"status\":\"SUCCESS\",\"amount\":$amt,\"tx\":\"$tx\",\"file_saved\":true}"
                        val out: OutputStream = socket.getOutputStream()
                        val response = "HTTP/1.1 200 OK\r\n" +
                                "Content-Type: application/json\r\n" +
                                "Access-Control-Allow-Origin: *\r\n" +
                                "Content-Length: ${responseBody.toByteArray().size}\r\n" +
                                "Connection: close\r\n\r\n" +
                                responseBody
                        out.write(response.toByteArray())
                        out.flush()
                    }
                    // Route 3: Web Portal Root
                    else {
                        val responseBody = "<!DOCTYPE html><html><head><title>AirUPI Local File Portal</title><style>body{font-family:sans-serif;background:#030712;color:#f8fafc;padding:20px;}a{color:#38bdf8;text-decoration:none;font-weight:bold;}.card{background:#0f172a;padding:15px;border-radius:10px;border:1px solid #1e293b;}</style></head><body><h2>📁 AirUPI Sovereign File Portal</h2><div class='card'><p>Local Soundbox Server is LIVE.</p><p><a href='/ledger.csv'>📥 Download Today's Ledger CSV</a></p></div></body></html>"
                        val out: OutputStream = socket.getOutputStream()
                        val response = "HTTP/1.1 200 OK\r\n" +
                                "Content-Type: text/html\r\n" +
                                "Access-Control-Allow-Origin: *\r\n" +
                                "Content-Length: ${responseBody.toByteArray().size}\r\n" +
                                "Connection: close\r\n\r\n" +
                                responseBody
                        out.write(response.toByteArray())
                        out.flush()
                    }
                }
                socket.close()
            } catch (_: Exception) {
                try { socket.close() } catch (_: Exception) {}
            }
        }
    }

    private fun appendLocalLedgerFile(amt: Int, lang: String, tx: String, token: String, source: String) {
        try {
            val dateStr = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(Date())
            val ledgerDir = File(filesDir, "ledger")
            if (!ledgerDir.exists()) ledgerDir.mkdirs()
            
            val csvFile = File(ledgerDir, "AirUPI_Daily_Ledger.csv")
            val isNew = !csvFile.exists()
            val writer = FileWriter(csvFile, true)
            if (isNew) {
                writer.append("Timestamp,Transaction_ID,Amount_INR,Language,TOTP_Token,Channel_Source,Status\n")
            }
            writer.append("$dateStr,$tx,$amt,$lang,$token,$source,VERIFIED_OFFLINE\n")
            writer.flush()
            writer.close()
        } catch (_: Exception) {}
    }

    private fun getLedgerCsvContent(): String {
        try {
            val csvFile = File(File(filesDir, "ledger"), "AirUPI_Daily_Ledger.csv")
            if (csvFile.exists()) {
                return csvFile.readText()
            }
        } catch (_: Exception) {}
        return "Timestamp,Transaction_ID,Amount_INR,Language,TOTP_Token,Channel_Source,Status\n"
    }

    private fun getDeviceIpAddress(): String {
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val iface = interfaces.nextElement()
                if (iface.isLoopback || !iface.isUp) continue
                val addresses = iface.inetAddresses
                while (addresses.hasMoreElements()) {
                    val addr = addresses.nextElement()
                    if (!addr.isLoopbackAddress && addr is Inet4Address) {
                        return addr.hostAddress ?: "127.0.0.1"
                    }
                }
            }
        } catch (_: Exception) {}
        return "127.0.0.1"
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            tts?.language = Locale("hi", "IN")
        }
    }

    inner class SoundboxBridge {
        @JavascriptInterface
        fun speak(text: String, lang: String) {
            runOnUiThread {
                val locale = when (lang.lowercase()) {
                    "hi" -> Locale("hi", "IN")
                    "ta" -> Locale("ta", "IN")
                    "te" -> Locale("te", "IN")
                    "kn" -> Locale("kn", "IN")
                    "bn" -> Locale("bn", "IN")
                    "mr" -> Locale("mr", "IN")
                    "gu" -> Locale("gu", "IN")
                    else -> Locale.ENGLISH
                }
                tts?.language = locale
                tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "AirUPISoundbox")
            }
        }

        @JavascriptInterface
        fun getDeviceIp(): String {
            return getDeviceIpAddress()
        }

        @JavascriptInterface
        fun getLocalLedgerCsv(): String {
            return getLedgerCsvContent()
        }

        @JavascriptInterface
        fun broadcastSubnetPayment(amt: Int, lang: String, tx: String, targetIp: String, token: String) {
            executor.execute {
                try {
                    val payload = "AIR_PAY:amt=$amt:lang=$lang:tx=$tx:token=$token\n".toByteArray()
                    
                    // 1. UDP Broadcast to Subnet
                    val broadcastAddr = InetAddress.getByName("255.255.255.255")
                    val udp = DatagramSocket()
                    udp.broadcast = true
                    val packet = DatagramPacket(payload, payload.size, broadcastAddr, 8088)
                    udp.send(packet)

                    if (targetIp.isNotEmpty() && targetIp != "127.0.0.1" && targetIp != "255.255.255.255") {
                        try {
                            val directAddr = InetAddress.getByName(targetIp)
                            val directPacket = DatagramPacket(payload, payload.size, directAddr, 8088)
                            udp.send(directPacket)
                        } catch (_: Exception) {}
                    }
                    udp.close()

                    // 2. Direct HTTP File-Drop Post
                    if (targetIp.isNotEmpty() && targetIp != "127.0.0.1") {
                        val url = URL("http://$targetIp:8080/drop?amt=$amt&lang=$lang&tx=$tx&token=$token")
                        val conn = url.openConnection() as HttpURLConnection
                        conn.connectTimeout = 800
                        conn.readTimeout = 800
                        conn.requestMethod = "GET"
                        conn.responseCode
                        conn.disconnect()
                    }

                    // 3. Bluetooth RFCOMM Broadcast (Airplane Mode)
                    val btManager = getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
                    val btAdapter = btManager?.adapter ?: BluetoothAdapter.getDefaultAdapter()
                    if (btAdapter != null && btAdapter.isEnabled) {
                        val pairedDevices = btAdapter.bondedDevices
                        for (device in pairedDevices) {
                            try {
                                val btClientSocket = device.createRfcommSocketToServiceRecord(AIR_UPI_BT_UUID)
                                btClientSocket.connect()
                                val out = btClientSocket.outputStream
                                out.write(payload)
                                out.flush()
                                btClientSocket.close()
                            } catch (_: Exception) {}
                        }
                    }
                } catch (_: Exception) {}
            }
        }

        @JavascriptInterface
        fun isUsbCableConnected(): Boolean {
            return isUsbConnected || (usbManager?.deviceList?.isNotEmpty() == true) || (usbManager?.accessoryList?.isNotEmpty() == true)
        }

        @JavascriptInterface
        fun getUsbStatus(): String {
            val count = (usbManager?.deviceList?.size ?: 0) + (usbManager?.accessoryList?.size ?: 0)
            return if (isUsbConnected || count > 0) {
                "CONNECTED ($count USB Devices / Endpoints Online)"
            } else {
                "READY / LISTENING ON PORT 8089"
            }
        }

        @JavascriptInterface
        fun sendUsbCablePayment(amt: Int, lang: String, tx: String, token: String) {
            executor.execute {
                try {
                    val payloadStr = "AIR_PAY:amt=$amt:lang=$lang:tx=$tx:token=$token\n"
                    val payload = payloadStr.toByteArray()

                    val targetIps = mutableListOf("192.168.42.129", "192.168.42.1", "192.168.43.1", "192.168.44.1", "10.0.0.1", "127.0.0.1")
                    
                    try {
                        val interfaces = NetworkInterface.getNetworkInterfaces()
                        while (interfaces.hasMoreElements()) {
                            val iface = interfaces.nextElement()
                            val addrs = iface.inetAddresses
                            while (addrs.hasMoreElements()) {
                                val a = addrs.nextElement()
                                if (a is Inet4Address && !a.isLoopbackAddress) {
                                    val parts = a.hostAddress?.split(".")
                                    if (parts != null && parts.size == 4) {
                                        targetIps.add("${parts[0]}.${parts[1]}.${parts[2]}.1")
                                        targetIps.add("${parts[0]}.${parts[1]}.${parts[2]}.129")
                                        targetIps.add("${parts[0]}.${parts[1]}.${parts[2]}.2")
                                    }
                                }
                            }
                        }
                    } catch (_: Exception) {}

                    for (ip in targetIps.distinct()) {
                        executor.execute {
                            try {
                                val s = Socket()
                                s.connect(InetSocketAddress(ip, 8089), 250)
                                val out = s.getOutputStream()
                                out.write(payload)
                                out.flush()
                                s.close()
                            } catch (_: Exception) {}
                        }
                    }

                    try {
                        val udp = DatagramSocket()
                        udp.broadcast = true
                        val broadcastAddr = InetAddress.getByName("255.255.255.255")
                        val p = DatagramPacket(payload, payload.size, broadcastAddr, 8089)
                        udp.send(p)
                        udp.close()
                    } catch (_: Exception) {}

                    // Loopback instant trigger for single-device test harness
                    processRawPacket(payloadStr.trim(), "Type-C Hardwired Vault")

                } catch (_: Exception) {}
            }
        }

        @JavascriptInterface
        fun startSensorLaboratory() {
            sensorManager?.let { sm ->
                magneticSensor?.let { sm.registerListener(this@MainActivity, it, SensorManager.SENSOR_DELAY_UI) }
                accelSensor?.let { sm.registerListener(this@MainActivity, it, SensorManager.SENSOR_DELAY_UI) }
                lightSensor?.let { sm.registerListener(this@MainActivity, it, SensorManager.SENSOR_DELAY_UI) }
            }
        }

        @JavascriptInterface
        fun stopSensorLaboratory() {
            sensorManager?.unregisterListener(this@MainActivity)
        }

        @JavascriptInterface
        fun transmitMagneticPulse(amt: Int) {
            executor.execute {
                try {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        val timings = longArrayOf(0, 100, 50, 100, 50, 150)
                        val amplitudes = intArrayOf(0, 255, 0, 255, 0, 255)
                        vibrator?.vibrate(VibrationEffect.createWaveform(timings, amplitudes, -1))
                    } else {
                        @Suppress("DEPRECATION")
                        vibrator?.vibrate(longArrayOf(0, 100, 50, 100, 50, 150), -1)
                    }
                    val tx = "AIR_MAG_${System.currentTimeMillis() % 10000}"
                    broadcastSubnetPayment(amt, "hi", tx, "", "847")
                } catch (_: Exception) {}
            }
        }

        @JavascriptInterface
        fun transmitSeismicTap(amt: Int) {
            executor.execute {
                try {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        val timings = longArrayOf(0, 80, 70, 80, 70, 120)
                        val amplitudes = intArrayOf(0, 255, 0, 255, 0, 255)
                        vibrator?.vibrate(VibrationEffect.createWaveform(timings, amplitudes, -1))
                    } else {
                        @Suppress("DEPRECATION")
                        vibrator?.vibrate(longArrayOf(0, 80, 70, 80, 70, 120), -1)
                    }
                    val tx = "AIR_SEISMIC_${System.currentTimeMillis() % 10000}"
                    broadcastSubnetPayment(amt, "hi", tx, "", "912")
                } catch (_: Exception) {}
            }
        }

        @JavascriptInterface
        fun transmitLuxFlash(amt: Int) {
            executor.execute {
                try {
                    mainCameraId?.let { cid ->
                        for (i in 0..3) {
                            cameraManager?.setTorchMode(cid, true)
                            Thread.sleep(45)
                            cameraManager?.setTorchMode(cid, false)
                            Thread.sleep(45)
                        }
                    }
                    val tx = "AIR_LUX_${System.currentTimeMillis() % 10000}"
                    broadcastSubnetPayment(amt, "hi", tx, "", "345")
                } catch (_: Exception) {}
            }
        }
    }

    override fun onSensorChanged(event: SensorEvent?) {
        if (event == null) return
        val now = System.currentTimeMillis()

        when (event.sensor.type) {
            Sensor.TYPE_MAGNETIC_FIELD -> {
                val x = event.values[0]
                val y = event.values[1]
                val z = event.values[2]
                currentMag = Math.sqrt((x * x + y * y + z * z).toDouble())
                if (currentMag > 90.0 && (now - lastTriggerTime > 3000)) {
                    lastTriggerTime = now
                    processRawPacket("AIR_PAY:amt=6:lang=hi:tx=AIR_MAG_${now % 10000}:token=847", "Magnetic Bump Link")
                }
            }
            Sensor.TYPE_ACCELEROMETER -> {
                val ax = event.values[0]
                val ay = event.values[1]
                val az = event.values[2]
                currentAccel = Math.sqrt((ax * ax + ay * ay + az * az).toDouble())
                if (Math.abs(currentAccel - 9.8) > 3.8 && (now - lastTriggerTime > 3000)) {
                    lastTriggerTime = now
                    processRawPacket("AIR_PAY:amt=6:lang=hi:tx=AIR_SEISMIC_${now % 10000}:token=912", "Seismic Table-Tap")
                }
            }
            Sensor.TYPE_LIGHT -> {
                currentLux = event.values[0].toDouble()
                if (currentLux > 500.0 && (now - lastTriggerTime > 3000)) {
                    lastTriggerTime = now
                    processRawPacket("AIR_PAY:amt=6:lang=hi:tx=AIR_LUX_${now % 10000}:token=345", "Optical Lux Strobe")
                }
            }
        }

        if (now - lastTelemetryDispatch > 45) {
            lastTelemetryDispatch = now
            runOnUiThread {
                val js = "if (window.onSensorTelemetry) window.onSensorTelemetry({ mag: ${"%.1f".format(Locale.US, currentMag)}, accel: ${"%.2f".format(Locale.US, currentAccel)}, lux: ${"%.1f".format(Locale.US, currentLux)} });"
                webView?.evaluateJavascript(js, null)
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    override fun onDestroy() {
        isMeshRunning = false
        try { sensorManager?.unregisterListener(this) } catch (_: Exception) {}
        try { unregisterReceiver(usbReceiver) } catch (_: Exception) {}
        try { serverSocket?.close() } catch (_: Exception) {}
        try { usbVaultServerSocket?.close() } catch (_: Exception) {}
        try { udpSocket?.close() } catch (_: Exception) {}
        try { bluetoothServerSocket?.close() } catch (_: Exception) {}
        tts?.stop()
        tts?.shutdown()
        super.onDestroy()
    }
}
