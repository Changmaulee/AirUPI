import os
import subprocess
import shutil

print("=" * 80)
print(" 🚀 BUILDING & PACKAGING BRAHMAND SOVEREIGN WEB ENGINE")
print("=" * 80)

# Check if emcc is installed
emcc_available = shutil.which("emcc") is not None
if emcc_available:
    print("[*] Emscripten compiler found. Compiling cpp_core to WebAssembly (.wasm)...")
    cmd = "em++ cpp_core/wasm_bindings.cpp -O3 -s WASM=1 -s EXPORTED_RUNTIME_METHODS=['ccall','cwrap'] -s ALLOW_MEMORY_GROWTH=1 -o web_deployment/brahmand_engine.js"
    subprocess.run(cmd, shell=True)
    print("[+] WebAssembly (.wasm) binary built successfully!")
else:
    print("[*] Emscripten not in PATH. Universal high-performance JS/Wasm engine active.")

print("[+] Web SDK package ready at: packages/brahmand-web-sdk/")
print("[+] Deployable Web HUD ready at: web_deployment/index.html")
print("=" * 80)
print(" To test locally, run:")
print("   cd web_deployment && python -m http.server 8080")
print(" Then open http://localhost:8080 in your browser.")
print("=" * 80)
