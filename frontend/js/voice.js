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

        // Check frequency: 1x per period (Morning, Afternoon, Night)
        const now = new Date();
        const hour = now.getHours();
        const dateStr = now.toISOString().split('T')[0]; // YYYY-MM-DD

        let period = '';
        if (hour < 12) period = 'morning';
        else if (hour < 18) period = 'afternoon';
        else period = 'night';

        const lastAlertKey = `jarvis_last_alert_${period}`;
        const lastAlertDate = localStorage.getItem(lastAlertKey);

        // If already spoke in this period today, skip
        if (lastAlertDate === dateStr) {
            console.log(`Jarvis already spoke in the ${period} of ${dateStr}. Skipping.`);
            return;
        }

        // 1. Initial Greeting
        let greeting = 'Olá';
        if (period === 'morning') greeting = 'Bom dia';
        else if (period === 'afternoon') greeting = 'Boa tarde';
        else greeting = 'Boa noite';

        const firstName = userName.split(' ')[0];

        // Polite greeting as requested
        this.speak(`${greeting}, ${firstName}. Espero que esteja tudo bem.`);

        // 2. Strict Reporting: Only Vencidos or Proximo 30
        const criticalItems = expiringItems.filter(item =>
            item.status === 'vencido' || item.status === 'proximo_30'
        );

        if (criticalItems.length > 0) {
            // Speak only up to 3 items
            const limit = Math.min(criticalItems.length, 3);

            for (let i = 0; i < limit; i++) {
                const item = criticalItems[i];
                const days = item.dias_para_vencer;
                let text = '';

                if (days < 0) {
                    text = `O equipamento ${item.descricao}, número de série ${item.numero_serie || 'não informado'}, está vencido.`;
                } else {
                    text = `O equipamento ${item.descricao}, certificado ${item.numero_certificado || 'não informado'}, está com ${days} dias para vencer.`;
                }
                this.speak(text);
            }

            if (criticalItems.length > 3) {
                const remaining = criticalItems.length - 3;
                this.speak(`E existem outros ${remaining} equipamentos em estado crítico.`);
            }

            // Mark as spoken for this period
            localStorage.setItem(lastAlertKey, dateStr);
        } else if (stats.vencidos === 0 && stats.vence_30_dias === 0) {
            this.speak("Todos os equipamentos estão em dia. Excelente trabalho.");
            localStorage.setItem(lastAlertKey, dateStr);
        }
    }
};

// Initialize on load
VoiceService.init();
