async function loadPiper() {
    const Piper = await import("piper-wasm/lib/index.js");

    function onInit(generate) {
        const utterance = new SpeechSynthesisUtterance("Hello, World!");
        generate(utterance);
    }

    const piper = new Piper('path_to_model.data', onInit);
}

loadPiper();