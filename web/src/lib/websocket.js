const opcodes = {
    0: 'DISPATCH',
    1: 'HEARTBEAT',
    2: 'HEARTBEAT_ACK',
    3: 'IDENTIFY',
    4: 'HELLO'
}


export default class WS {
    url;
    token;
    ws;
    heartbeatInterval;
    heartbeatTask;

    constructor(url) {
        this.url = url;
    }

    send(opcode, data = null) {
        const message = {
            opcode: opcode,
            data: data
        }
        const raw_message = JSON.stringify(message);
        console.log(`Sending message with opcode ${opcode} ${opcodes[opcode]}...`)
        this.ws.send(raw_message);
    }

    connect(token) {
        this.token = token;

        console.log('Connecting to WS...')
        this.ws  = new WebSocket(this.url);

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(`Received message with opcode ${data.opcode} ${opcodes[data.opcode]}.`);
            console.log(data);

            if (data.opcode === 4) {
                this.handleHello(data.data);
            } else if (data.opcode === 0) {
                this.handleDispatch(data.event_name, data.data);
            }
        }

        this.ws.onopen = (event) => {
            console.log('Websocket connection opened.')
        }

        this.ws.onclose = (event) => {
            console.log(`Websocket connection closed with code ${event.code}.`)
            this.onDisconnect()
        }
    }

    onDispatch(event, data) {}

    onConnect() {}

    onDisconnect() {}

    handleDispatch(event, data) {
        console.log(`received event: ${event}`);
        console.log(data);
        this.onDispatch(event, data);
    }

    handleHello(data) {
        this.heartbeatInterval = data.heartbeat_interval;
        console.log(`Heartbeat interval is ${this.heartbeatInterval}ms.`);
        this.heartbeat();
        this.identify();
        this.onConnect();
    }

    identify() {
        this.send(3, {token: this.token});
    }

    heartbeat = () => {
        this.send(1);
        this.heartbeatTask = setTimeout(this.heartbeat, this.heartbeatInterval);
    }

    close(code = 1000) {
        console.log(`Closing connection with code ${code}.`);
        if (this.heartbeatTask) {
            clearTimeout(this.heartbeatTask);
        }
        this.ws.close(code);
    }
}
