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
    async greetUser(userName, stats, expiringItems = []) {
        // Stop any previous speech
        this.synth.cancel();

        // 1. Initial Greeting
        const hour = new Date().getHours();
        let greeting = 'Olá';
        if (hour < 12) greeting = 'Bom dia';
        else if (hour < 18) greeting = 'Boa tarde';
        else greeting = 'Boa noite';

        const firstName = userName.split(' ')[0];

        // Polite intro as requested
        this.speak(`${greeting}, ${firstName}. Espero que esteja tudo bem.`);

        // 2. Critical/Warning with Details
        if (expiringItems.length > 0) {
            // "O equipamento tal, certificado tal, esta com X dias para vencer"

            // Speak only up to 3 items to avoid fatigue
            const limit = Math.min(expiringItems.length, 3);

            for (let i = 0; i < limit; i++) {
                const item = expiringItems[i];
                const days = item.dias_para_vencer;
                const text = `O equipamento ${item.descricao}, certificado ${item.numero_certificado || 'não informado'}, está com ${days} dias para vencer.`;
                this.speak(text);
            }

            if (expiringItems.length > 3) {
                const remaining = expiringItems.length - 3;
                this.speak(`E existem outros ${remaining} equipamentos requerendo atenção.`);
            }
        }
        else if (stats.vencidos === 0 && stats.vence_30_dias === 0) {
            this.speak("Todos os equipamentos estão em dia. Bom trabalho.");
        }
    }
};

// Initialize on load
VoiceService.init();
