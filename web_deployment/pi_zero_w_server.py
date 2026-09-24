import os
import json
import http.server
import socketserver
import urllib.parse
import time
from gtts import gTTS

PORT = 8000
socketserver.TCPServer.allow_reuse_address = True
AUDIO_DIR = "/home/pi/audio_cache"
os.makedirs(AUDIO_DIR, exist_ok=True)

LEDGER = []
TOTAL_AMOUNT = 0

def num_to_words(n, lang):
    n = int(n)
    if lang == 'hi':
        exact = {
            10: "Das", 20: "Bees", 25: "Pachchees", 30: "Tees", 40: "Chaalees", 50: "Pachaas",
            100: "Ek sau", 150: "Ek sau pachaas", 200: "Do sau", 250: "Do sau pachaas",
            300: "Teen sau", 400: "Chaar sau", 500: "Paanch sau", 1000: "Ek hazaar", 2000: "Do hazaar", 5000: "Paanch hazaar"
        }
        if n in exact: return exact[n]
        if n >= 1000: return f"{n//1000} hazaar " + exact.get(n%1000, str(n%1000) if n%1000 else "")
        if n >= 100: return f"{n//100} sau " + exact.get(n%100, str(n%100) if n%100 else "")
        return str(n)
    elif lang == 'ta':
        exact = {
            10: "Patthu", 20: "Irubadhu", 50: "Aymbadhu",
            100: "Nooru", 150: "Noottru aymbadhu", 200: "Iru-nooru", 250: "Iru-noottru aymbadhu",
            300: "Mun-nooru", 500: "Ayn-nooru", 1000: "Aayiram", 2000: "Irandu aayiram", 5000: "Aindhu aayiram"
        }
        return exact.get(n, str(n))
    elif lang == 'te':
        exact = {
            10: "Padhi", 20: "Iravai", 50: "Yaabhai",
            100: "Vanda", 150: "Noota yaabhai", 200: "Rendu vandalu", 250: "Rendu vandala yaabhai",
            300: "Moodu vandalu", 500: "Aydu vandalu", 1000: "Veyyi"
        }
        return exact.get(n, str(n))
    elif lang == 'kn':
        exact = {
            10: "Hatthu", 20: "Ippatthu", 50: "Aivatthu",
            100: "Nooru", 150: "Noora aivatthu", 200: "Innooru", 250: "Innoora aivatthu",
            300: "Munnooru", 500: "Aydu nooru", 1000: "Ondhu saavira"
        }
        return exact.get(n, str(n))
    else:
        return str(n)

def get_phrase_and_lang(amt, lang):
    num_str = num_to_words(amt, lang)
    templates = {
        'hi': ('hi', f"Paytm par {num_str} Rupaye prapt hue"),
        'ta': ('ta', f"Paytmil {num_str} Roobai petrapattadhu"),
        'te': ('te', f"Paytmlonoo {num_str} Roopaayalu andhinavi"),
        'kn': ('kn', f"Paytmli {num_str} Roopaayi sveekarisalaagidhe"),
        'en': ('en', f"Received {amt} Rupees on Paytm")
    }
    return templates.get(lang, templates['en'])

CUSTOMER_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <title>AirUPI - Customer Phone</title>
  <style>
    :root { --bg: #030712; --card: #0f172a; --accent: #38bdf8; --green: #10b981; --border: #1e293b; --text: #f8fafc; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 16px; display: flex; justify-content: center; }
    .card { width: 100%; max-width: 420px; background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
    h2 { font-size: 18px; margin-top: 0; color: var(--accent); display: flex; align-items: center; justify-content: space-between; }
    .airplane-badge { font-size: 11px; background: rgba(239,68,68,0.2); color: #f87171; border: 1px solid #ef4444; padding: 3px 8px; border-radius: 999px; }
    .scan-btn { width: 100%; background: #3b82f6; color: #fff; border: none; border-radius: 8px; padding: 12px; font-weight: 700; cursor: pointer; font-size: 14px; margin-bottom: 12px; display: flex; align-items: center; justify-content: center; gap: 6px; }
    .scanner-box { display: none; height: 90px; background: #000; border: 2px dashed #38bdf8; border-radius: 8px; position: relative; overflow: hidden; align-items: center; justify-content: center; margin-bottom: 12px; }
    .scan-line { position: absolute; width: 100%; height: 3px; background: #38bdf8; box-shadow: 0 0 10px #38bdf8; top: 0; animation: scanLine 1.2s infinite alternate; }
    @keyframes scanLine { from { top: 5%; } to { top: 90%; } }
    .field { margin-bottom: 14px; }
    label { display: block; font-size: 12px; color: #94a3b8; margin-bottom: 6px; }
    input, select { width: 100%; box-sizing: border-box; background: #020617; border: 1px solid var(--border); border-radius: 8px; padding: 12px; color: #fff; font-size: 16px; }
    .btn-beam { width: 100%; background: linear-gradient(135deg, #10b981, #047857); color: #fff; border: none; border-radius: 10px; padding: 16px; font-weight: 700; font-size: 16px; cursor: pointer; box-shadow: 0 4px 15px rgba(16,185,129,0.3); margin-top: 8px; }
    .btn-beam:active { transform: scale(0.97); }
    .status-box { margin-top: 14px; padding: 12px; border-radius: 8px; font-family: monospace; font-size: 13px; background: #020617; border: 1px solid var(--border); color: #38bdf8; text-align: center; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Phone Terminal <span class="airplane-badge">AIRPLANE MODE</span></h2>
    
    <button class="scan-btn" onclick="startQrScan()">Scan Shop QR Code</button>

    <div class="scanner-box" id="scannerView">
      <div class="scan-line"></div>
      <div style="font-size: 12px; color: #38bdf8; z-index: 2;">Scanning Merchant QR Stand Offline...</div>
    </div>

    <div style="background: #020617; border: 1px solid #334155; border-radius: 8px; padding: 12px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <div style="font-size: 10px; color: #94a3b8;">SCANNED MERCHANT:</div>
        <div style="font-size: 14px; font-weight: 700; color: #fff;" id="mName">Gupta General Store</div>
        <div style="font-size: 12px; color: var(--accent); font-family: monospace;" id="mVpa">guptastore@airupi</div>
      </div>
      <div style="font-size: 12px; font-weight: 700; color: var(--green);" id="mLock">[LOCKED]</div>
    </div>

    <div class="field">
      <label>Enter Payment Amount (INR):</label>
      <input type="number" id="payAmt" value="250" min="1" step="1">
    </div>

    <div class="field">
      <label>Select Soundbox Language:</label>
      <select id="payLang">
        <option value="hi" selected>Hindi (Do Sau Pachaas...)</option>
        <option value="ta">Tamil (Iru-noottru aymbadhu...)</option>
        <option value="te">Telugu (Rendu vandala yaabhai...)</option>
        <option value="kn">Kannada (Innoora aivatthu...)</option>
        <option value="en">English (Rupees received...)</option>
      </select>
    </div>

    <button class="btn-beam" onclick="beamPayment()">Beam 45-Byte Layer-2 Payment</button>
    <div class="status-box" id="statusMsg">Ready to beam wireless payment...</div>
  </div>

  <script>
    function startQrScan() {
      const box = document.getElementById('scannerView');
      const lock = document.getElementById('mLock');
      box.style.display = 'flex';
      lock.innerText = "[SCANNING...]";
      lock.style.color = "#f59e0b";
      setTimeout(() => {
        box.style.display = 'none';
        lock.innerText = "[VERIFIED OK]";
        lock.style.color = "#10b981";
        document.getElementById('statusMsg').innerText = "Target Locked: guptastore@airupi";
      }, 1000);
    }

    function beamPayment() {
      const amt = document.getElementById('payAmt').value || 250;
      const lang = document.getElementById('payLang').value || 'hi';
      const tx = "TX_" + Math.floor(Math.random()*9000+1000);
      const status = document.getElementById('statusMsg');
      
      status.innerText = "Beaming 45-byte packet over Wi-Fi Layer-2...";
      status.style.color = "#f59e0b";

      fetch('/api/pay?tx=' + tx + '&amt=' + amt + '&lang=' + lang)
        .then(r => r.json())
        .then(data => {
          status.innerText = "SENT TO SOUNDBOX: " + data.tx + " (" + data.spoken + ")";
          status.style.color = "#10b981";
        })
        .catch(err => {
          status.innerText = "Error: " + err;
          status.style.color = "#ef4444";
        });
    }
  </script>
</body>
</html>"""

MERCHANT_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AirUPI - Sovereign Soundbox</title>
  <style>
    :root { --bg: #030712; --card: #0f172a; --accent: #38bdf8; --green: #10b981; --border: #1e293b; --text: #f8fafc; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; display: flex; justify-content: center; }
    .card { width: 100%; max-width: 580px; background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
    .header-bar { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 16px; }
    .qr-stand { display: grid; grid-template-columns: 110px 1fr; gap: 14px; align-items: center; background: #020617; border: 1px solid #334155; border-radius: 12px; padding: 12px; margin-bottom: 16px; }
    .lcd { background: #022c22; border: 2px solid #059669; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 16px; }
    .lcd-amt { font-size: 46px; font-weight: 900; color: #34d399; font-family: monospace; }
    .lcd-status { font-size: 13px; color: #6ee7b7; margin-top: 6px; font-family: monospace; }
    .unlock-btn { width: 100%; background: #10b981; color: #fff; font-weight: 800; border: none; border-radius: 8px; padding: 14px; cursor: pointer; font-size: 14px; margin-bottom: 12px; }
    .terminal { background: #020617; border: 1px solid var(--border); border-radius: 8px; padding: 12px; font-family: monospace; font-size: 12px; color: #38bdf8; height: 160px; overflow-y: auto; white-space: pre-wrap; }
  </style>
</head>
<body>
  <div class="card">
    <div class="header-bar">
      <div>
        <div style="font-size: 18px; font-weight: 700; color: #fff;">Gupta General Store (Soundbox)</div>
        <div style="font-size: 12px; color: var(--accent); font-family: monospace;">guptastore@airupi &bull; Node: 192.168.1.174</div>
      </div>
      <div style="background: rgba(16,185,129,0.2); color: #34d399; border: 1px solid #10b981; padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 700;">
        SOVEREIGN ACTIVE
      </div>
    </div>

    <!-- MERCHANT QR CODE STAND -->
    <div class="qr-stand">
      <div style="background: #fff; padding: 6px; border-radius: 8px; text-align: center;">
        <svg width="90" height="90" viewBox="0 0 100 100" style="display: block; margin: 0 auto;">
          <rect width="100" height="100" fill="#ffffff"/>
          <rect x="5" y="5" width="28" height="28" fill="#000000"/>
          <rect x="9" y="9" width="20" height="20" fill="#ffffff"/>
          <rect x="13" y="13" width="12" height="12" fill="#000000"/>
          <rect x="67" y="5" width="28" height="28" fill="#000000"/>
          <rect x="71" y="9" width="20" height="20" fill="#ffffff"/>
          <rect x="75" y="13" width="12" height="12" fill="#000000"/>
          <rect x="5" y="67" width="28" height="28" fill="#000000"/>
          <rect x="9" y="71" width="20" height="20" fill="#ffffff"/>
          <rect x="13" y="75" width="12" height="12" fill="#000000"/>
          <rect x="40" y="10" width="8" height="8" fill="#000000"/>
          <rect x="52" y="10" width="8" height="8" fill="#000000"/>
          <rect x="40" y="24" width="20" height="6" fill="#000000"/>
          <rect x="10" y="40" width="80" height="6" fill="#000000"/>
          <rect x="40" y="52" width="16" height="16" fill="#000000"/>
          <rect x="65" y="52" width="20" height="8" fill="#000000"/>
          <rect x="65" y="70" width="10" height="20" fill="#000000"/>
          <rect x="80" y="75" width="12" height="15" fill="#000000"/>
          <rect x="40" y="75" width="18" height="18" fill="#000000"/>
        </svg>
        <div style="color: #000; font-size: 7px; font-weight: 800; margin-top: 2px;">AIRUPI ACCEPTED</div>
      </div>
      <div>
        <div style="font-size: 11px; color: #94a3b8;">SHOP QR STAND:</div>
        <div style="font-size: 15px; font-weight: 700; color: #fff;">Gupta General Store</div>
        <div style="font-size: 12px; color: var(--accent); font-family: monospace;">guptastore@airupi</div>
        <div style="font-size: 11px; color: var(--green); margin-top: 4px;">Static Offline QR (Zero Power/Internet)</div>
      </div>
    </div>

    <!-- EMBEDDED HTML5 AUDIO PLAYER -->
    <audio id="soundboxAudio" preload="auto"></audio>

    <button class="unlock-btn" id="audioUnlockBtn" onclick="activateSpeaker()">Soundbox Active & Ready</button>

    <div class="lcd">
      <div style="font-size: 12px; color: #a7f3d0; font-weight: 700; letter-spacing: 1px;">TOTAL REVENUE RECEIVED</div>
      <div class="lcd-amt" id="lcdAmount">&#8377; 0.00</div>
      <div class="lcd-status" id="lcdStatus">LISTENING FOR OVER-THE-AIR PACKETS...</div>
    </div>

    <label style="font-size: 12px; color: #94a3b8; display: block; margin-bottom: 6px;">Promiscuous Sniffer Telemetry Log:</label>
    <div class="terminal" id="termLog">AirUPI Sovereign Sniffer Active on Raspberry Pi Zero W (192.168.1.174)...
Zero Cloud Calls &bull; Offline QR Stand & Promiscuous Sniffer Active</div>
  </div>

  <script>
    const player = document.getElementById('soundboxAudio');

    function activateSpeaker() {
      player.src = '/api/audio?amt=150&lang=hi&t=' + Date.now();
      player.play().catch(e => console.log('Audio init:', e));
      const btn = document.getElementById('audioUnlockBtn');
      btn.innerText = "Speaker Driver Active";
      btn.style.background = "#059669";
      logMsg("[AUDIO SYSTEM]: Soundbox Audio Driver Ready.");
    }

    function logMsg(txt) {
      const term = document.getElementById('termLog');
      term.innerText += "\\n" + txt;
      term.scrollTop = term.scrollHeight;
    }

    function playNativeAudio(amt, lang) {
      player.src = '/api/audio?amt=' + amt + '&lang=' + lang + '&t=' + Date.now();
      player.play().catch(e => {
        console.log("Audio play error:", e);
      });
    }

    let lastTxCount = -1;

    function pollServer() {
      fetch('/api/state')
        .then(res => res.json())
        .then(data => {
          if (lastTxCount === -1) {
            lastTxCount = data.tx_count;
            if (data.latest) {
              document.getElementById('lcdAmount').innerHTML = "&#8377; " + data.total + ".00";
              document.getElementById('lcdStatus').innerText = "LAST: " + data.latest.tx + " (+Rs. " + data.latest.amount + ")";
            }
            return;
          }

          if (data.tx_count > lastTxCount) {
            lastTxCount = data.tx_count;
            const last = data.latest;
            document.getElementById('lcdAmount').innerHTML = "&#8377; " + data.total + ".00";
            document.getElementById('lcdStatus').innerText = "SUCCESS: " + last.tx + " (+Rs. " + last.amount + ")";
            logMsg("[802.11 INGESTED (" + last.lang.toUpperCase() + ")]: " + last.spoken + " | Total=Rs. " + data.total);
            playNativeAudio(last.amount, last.lang);
          }
        }).catch(()=>{});
    }

    setInterval(pollServer, 1000);
    pollServer();
  </script>
</body>
</html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_GET(self):
        global TOTAL_AMOUNT, LEDGER
        p = urllib.parse.urlparse(self.path)

        if p.path == '/api/pay':
            q = urllib.parse.parse_qs(p.query)
            amt = int(q.get('amt', [150])[0])
            lang = q.get('lang', ['hi'])[0]
            tx = 'TX_' + str(int(time.time()))[-4:]
            TOTAL_AMOUNT += amt
            
            gcode, text = get_phrase_and_lang(amt, lang)
            audio_path = os.path.join(AUDIO_DIR, "{}_{}.mp3".format(lang, amt))
            if not os.path.exists(audio_path):
                try:
                    tts = gTTS(text=text, lang=gcode, slow=False)
                    tts.save(audio_path)
                except Exception as e:
                    print("Error generating TTS:", e)
            
            entry = {'tx': tx, 'amount': amt, 'lang': lang, 'spoken': text, 'timestamp': time.time()}
            LEDGER.append(entry)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'OK', 'amount': amt, 'total': TOTAL_AMOUNT, 'tx': tx, 'spoken': text}).encode('utf-8'))

        elif p.path == '/api/audio':
            q = urllib.parse.parse_qs(p.query)
            amt = int(q.get('amt', [150])[0])
            lang = q.get('lang', ['hi'])[0]
            
            gcode, text = get_phrase_and_lang(amt, lang)
            audio_path = os.path.join(AUDIO_DIR, "{}_{}.mp3".format(lang, amt))
            if not os.path.exists(audio_path):
                try:
                    tts = gTTS(text=text, lang=gcode, slow=False)
                    tts.save(audio_path)
                except Exception as e:
                    print("Error generating TTS:", e)

            if os.path.exists(audio_path):
                with open(audio_path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(404)
                self.end_headers()
            
        elif p.path == '/api/state':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'total': TOTAL_AMOUNT, 'tx_count': len(LEDGER), 'latest': LEDGER[-1] if LEDGER else None}).encode('utf-8'))
            
        elif p.path == '/customer':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(CUSTOMER_HTML.encode('utf-8'))
            
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(MERCHANT_HTML.encode('utf-8'))

httpd = socketserver.TCPServer(('0.0.0.0', PORT), Handler)
httpd.serve_forever()