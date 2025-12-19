/**
 * CalibraCore Lab - Voice Assistant ("Jarvis")
 */

const VoiceService = {
    synth: window.speechSynthesis,
    voice: null,
    speaking: false,

    // Helper: Number to Words PT-BR
    numberToWords(n) {
        if (typeof n !== "number" || !Number.isFinite(n)) return String(n);
        n = Math.trunc(n);

        if (n === 0) return "zero";
        if (n < 0) return "menos " + this.numberToWords(Math.abs(n));

        const unidades = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"];
        const dezADezenove = ["dez", "onze", "doze", "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"];
        const dezenas = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"];
        const centenas = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos"];

        const ate999 = (x) => {
            if (x === 0) return "";
            if (x === 100) return "cem";

            const c = Math.floor(x / 100);
            const r = x % 100;
            const d = Math.floor(r / 10);
            const u = r % 10;

            let parts = [];
            if (c > 0) parts.push(centenas[c]);
            if (r > 0) {
                if (r >= 10 && r <= 19) {
                    parts.push(dezADezenove[r - 10]);
                } else {
                    if (d > 0) parts.push(dezenas[d]);
                    if (u > 0) parts.push(unidades[u]);
                }
            }
            if (parts.length <= 1) return parts.join("");
            if (parts.length === 2) return parts[0] + " e " + parts[1];
            return parts[0] + " e " + parts.slice(1).join(" e ");
        };

        const milhoes = Math.floor(n / 1_000_000);
        const milhares = Math.floor((n % 1_000_000) / 1000);
        const resto = n % 1000;

        let out = [];
        if (milhoes > 0) {
            out.push(milhoes === 1 ? "um milhão" : `${ate999(milhoes)} milhões`);
        }
        if (milhares > 0) {
            out.push(milhares === 1 ? "mil" : `${ate999(milhares)} mil`);
        }
        if (resto > 0) {
            if (out.length > 0 && resto < 100) out.push("e " + ate999(resto));
            else out.push(ate999(resto));
        }
        return out.join(" ").replace(/\s+/g, " ").trim();
    },

    // Helper: Date to Words PT-BR
    dateToWords(isoDate) {
        const months = [
            "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
        ];
        const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(isoDate));
        if (!m) return String(isoDate);

        const year = Number(m[1]);
        const month = Number(m[2]);
        const day = Number(m[3]);

        const dayW = this.numberToWords(day);
        const yearW = this.yearToWords(year);
        return `dia ${dayW} de ${months[month - 1]} de ${yearW}`;
    },

    yearToWords(year) {
        if (year < 1000 || year > 9999) return this.numberToWords(year);
        const mil = Math.floor(year / 1000);
        const resto = year % 1000;
        let parts = [];
        if (mil === 1) parts.push("mil");
        else if (mil === 2) parts.push("dois mil");
        else parts.push(this.numberToWords(mil) + " mil");

        if (resto === 0) return parts.join(" ");
        parts.push("e " + this.numberToWords(resto));
        return parts.join(" ").replace(/\s+/g, " ").trim();
    },

    /**
     * Initialize voices
     */
    init() {
        if (!this.synth) return;
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
        if (voices.length === 0) {
            console.warn('Jarvis: No voices available yet.');
            return;
        }

        this.voice = voices.find(v => v.name.includes('Google Português do Brasil')) ||
            voices.find(v => v.name.includes('Luciana')) ||
            voices.find(v => v.lang === 'pt-BR' || v.lang.startsWith('pt')) ||
            voices[0];

        console.log('Jarvis: Voice loaded ->', this.voice ? this.voice.name : 'None');
    },

    /**
     * Speak text
     */
    speak(text, priority = false) {
        if (!this.synth) return;

        // If voice not loaded, try to load it now
        if (!this.voice) this.loadVoice();
        if (!this.voice) {
            console.warn('Jarvis: Cannot speak, no voice loaded.');
            return;
        }

        if (priority) this.synth.cancel();

        console.log('Jarvis speaking:', text);
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = this.voice;
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        this.synth.speak(utterance);
    },

    /**
     * Greet user and report status
     */
    async greetUser(userName, stats, expiringItems = [], force = false) {
        console.log('Jarvis: greetUser called', { userName, stats, itemCount: expiringItems.length });
        this.synth.cancel();

        const now = new Date();
        const hour = now.getHours();
        const dateStr = now.toISOString().split('T')[0];

        let period = '';
        if (hour < 12) period = 'morning';
        else if (hour < 18) period = 'afternoon';
        else period = 'night';

        const lastAlertKey = `jarvis_last_alert_${period}`;
        const lastAlertDate = localStorage.getItem(lastAlertKey);

        if (lastAlertDate === dateStr && !force) {
            console.log(`Jarvis: already spoke in the ${period} of ${dateStr}. Use force=true to override.`);
            return;
        }

        const firstName = userName.split(' ')[0];

        // 1. Dynamic Greeting based on period
        if (period === 'morning') {
            this.speak(`Bom dia, ${firstName}. Seja bem-vindo ao CalibraCore Lab. Desejamos um excelente dia de trabalho, com segurança, precisão e conformidade técnica.`);
        } else if (period === 'afternoon') {
            this.speak(`Boa tarde, ${firstName}. O CalibraCore Lab segue acompanhando os prazos de calibração dos seus equipamentos para garantir conformidade operacional.`);
        } else {
            this.speak(`Boa noite, ${firstName}. O CalibraCore Lab permanece monitorando automaticamente os vencimentos de calibração, assegurando controle técnico e tranquilidade operacional.`);
        }

        // 2. Calibration Alerts Logic
        // We only speak about the most critical items found
        const items30 = expiringItems.filter(eq => eq.dias_para_vencer === 30);
        const items15_7 = expiringItems.filter(eq => eq.dias_para_vencer === 15 || eq.dias_para_vencer === 7);
        const itemsExpired = expiringItems.filter(eq => eq.dias_para_vencer <= 0);

        // Process up to 2 items per category to avoid being too long
        if (itemsExpired.length > 0) {
            itemsExpired.slice(0, 2).forEach(eq => {
                const dateW = this.dateToWords(eq.data_vencimento);
                this.speak(`${firstName}, atenção. O equipamento ${eq.descricao} – Certificado número ${this.numberToWords(Number(eq.numero_certificado) || 0)} está com a calibração vencida desde ${dateW}. Recomendamos suspender o uso para fins de medição e regularizar a recalibração.`);
            });
        }

        if (items30.length > 0) {
            const todayW = this.dateToWords(dateStr);
            items30.slice(0, 2).forEach(eq => {
                this.speak(`Informamos que, na data de ${todayW}, o equipamento ${eq.descricao} – Certificado número ${this.numberToWords(Number(eq.numero_certificado) || 0)} encontra-se a trinta dias do vencimento de sua calibração. Recomendamos entrar em contato com a empresa responsável para providenciar a emissão de um novo certificado.`);
            });
        }

        if (items15_7.length > 0) {
            items15_7.slice(0, 2).forEach(eq => {
                const daysW = this.numberToWords(eq.dias_para_vencer);
                this.speak(`${firstName}, bom dia. Atenção: o equipamento ${eq.descricao} – Certificado número ${this.numberToWords(Number(eq.numero_certificado) || 0)} vence em ${daysW} dias. Para manter a conformidade técnica, recomendamos agendar a recalibração.`);
            });
        }

        // 3. Final Check: All good
        if (itemsExpired.length === 0 && items30.length === 0 && items15_7.length === 0 && stats.vence_30_dias === 0 && stats.vencidos === 0) {
            this.speak("Excelente trabalho. Todos os seus equipamentos estão em conformidade técnica no momento.");
        }

        localStorage.setItem(lastAlertKey, dateStr);
    }
};

VoiceService.init();
