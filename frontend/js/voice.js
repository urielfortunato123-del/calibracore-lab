/**
 * CalibraCore Lab - Voice Assistant ("Jarvis")
 */

const VoiceService = {
    synth: window.speechSynthesis,
    voice: null,
    speaking: false,

    /**
     * Initialize voices
     */
    init() {
        if (!this.synth) {
            console.warn('Speech synthesis not supported');
            return;
        }

        // Wait for voices to load
        if (this.synth.onvoiceschanged !== undefined) {
            this.synth.onvoiceschanged = () => this.loadVoice();
        }
        this.loadVoice();
    },

    /**
     * Load Portuguese voice
     */
    loadVoice() {
        const voices = this.synth.getVoices();
        // Priority: Google Português do Brasil -> Microsoft Daniel -> Any PT-BR
        this.voice = voices.find(v => v.name.includes('Google Português do Brasil')) ||
            voices.find(v => v.name.includes('Luciana')) ||
            voices.find(v => v.lang === 'pt-BR') ||
            voices[0];

        console.log('Voice loaded:', this.voice ? this.voice.name : 'Default');
    },

    /**
     * Speak text
     */
    speak(text, priority = false) {
        if (!this.synth || !this.voice) return;

        if (priority) {
            this.synth.cancel();
        }

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = this.voice;
        utterance.rate = 1.0; // Normal speed
        utterance.pitch = 1.0; // Normal pitch
        utterance.volume = 1.0;

        this.synth.speak(utterance);
    },

    /**
     * Greet user and report status
     */
    async greetUser(userName, stats) {
        // Stop any previous speech
        this.synth.cancel();

        // 1. Initial Greeting
        const hour = new Date().getHours();
        let greeting = 'Olá';
        if (hour < 12) greeting = 'Bom dia';
        else if (hour < 18) greeting = 'Boa tarde';
        else greeting = 'Boa noite';

        const firstName = userName.split(' ')[0];

        // Construct message parts for natural flow
        const parts = [
            `${greeting}, ${firstName}.`,
            `O sistema Calibra Core está operante.`
        ];

        // 2. Critical Warnings (Vencidos)
        if (stats.vencidos > 0) {
            parts.push(`Atenção. Existem ${stats.vencidos} equipamentos vencidos que exigem sua ação imediata.`);
        }
        // 3. Warnings (Proximo 30/60)
        else if (stats.vence_30_dias > 0) {
            parts.push(`Nota. Você tem ${stats.vence_30_dias} equipamentos vencendo nos próximos trinta dias.`);
        }
        else {
            parts.push("Todos os equipamentos estão em dia.");
        }

        // Speak sequence with small pauses handled by the browser queue
        parts.forEach(part => this.speak(part));
    }
};

// Initialize on load
VoiceService.init();
