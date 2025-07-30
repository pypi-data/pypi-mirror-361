"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.LoopClient = void 0;
class LoopClient {
    constructor() {
        this.url = null;
        this.loopId = null;
        this.hasSchema = false;
        this.isPaused = false;
        this.error = null;
        this.eventCallback = null;
    }
    withLoop(options) {
        this.url = options.url;
        this.loopId = options.loopId || null;
        this.eventCallback = options.eventCallback || null;
        return this;
    }
    async setup() {
        if (!this.url) {
            throw new Error("Loop not configured - call withLoop first");
        }
        try {
            const eventTypes = await this.getEventTypes();
            this.hasSchema = true;
            return eventTypes;
        }
        catch (err) {
            throw err;
        }
    }
    async send(type, data) {
        if (!this.url) {
            throw new Error("Loop not configured - call withLoop first");
        }
        const eventData = {
            type,
            ...data,
        };
        if (this.loopId) {
            eventData.loop_id = this.loopId;
        }
        try {
            const response = await fetch(this.url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(eventData),
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            const result = await response.json();
            if (result && result.loop_id) {
                this.loopId = result.loop_id;
            }
            return {
                success: true,
                data: result,
            };
        }
        catch (err) {
            return {
                success: false,
                error: err instanceof Error ? err.message : "Unknown error",
            };
        }
    }
    // Fetch event type schemas
    async getEventTypes() {
        if (!this.url) {
            throw new Error("Loop not configured - call withLoop first");
        }
        try {
            const response = await fetch(this.url, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            return await response.json();
        }
        catch (err) {
            throw err;
        }
    }
    pause() {
        this.isPaused = true;
    }
    resume() {
        this.isPaused = false;
    }
    stop() { }
    getStatus() {
        return {
            hasSchema: this.hasSchema,
            isPaused: this.isPaused,
            error: this.error,
        };
    }
}
exports.LoopClient = LoopClient;
