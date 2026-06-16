const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const app = express();
const port = 3000;

app.use(express.json());

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

client.on('qr', (qr) => {
    console.log('QR RECEIVED. Please scan it using WhatsApp:');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('WhatsApp Client is ready!');
});

client.initialize();

app.post('/dispatch-message/', async (req, res) => {
    const { phone, message } = req.body;

    if (!phone || !message) {
        return res.status(400).json({ error: 'Phone and message are required fields.' });
    }

    // Clean phone number: remove non-numeric characters
    let cleanedPhone = phone.replace(/\D/g, '');

    // Assuming India prefix if 10 digits
    if (cleanedPhone.length === 10) {
        cleanedPhone = `91${cleanedPhone}`;
    }

    const chatId = `${cleanedPhone}@c.us`;

    try {
        // Resolve the exact serialized ID to prevent 'getChat' undefined errors on new contacts
        const numberId = await client.getNumberId(cleanedPhone);
        if (!numberId) {
            console.error(`Number not registered on WhatsApp: ${cleanedPhone}`);
            return res.status(404).json({ error: 'Number not registered on WhatsApp.' });
        }

        await client.sendMessage(numberId._serialized, message);
        console.log(`Message sent to ${numberId._serialized}`);
        res.status(200).json({ success: true, message: 'Message dispatched successfully.' });
    } catch (error) {
        console.error(`Failed to send message to ${cleanedPhone}:`, error);
        res.status(500).json({ error: 'Failed to send message.', details: error.toString(), stack: error.stack });
    }
});

app.listen(port, () => {
    console.log(`TinyCare SMS Gateway listening on port ${port}`);
});
