import { LoopResponse, EventCallback } from "./types";
export declare class LoopClient {
    private url;
    private loopId;
    private hasSchema;
    private isPaused;
    private error;
    private eventCallback;
    constructor();
    withLoop(options: {
        url: string;
        eventCallback?: EventCallback;
        loopId?: string;
    }): LoopClient;
    setup(): Promise<Record<string, any>>;
    send(type: string, data: Record<string, any>): Promise<LoopResponse>;
    getEventTypes(): Promise<Record<string, any>>;
    pause(): void;
    resume(): void;
    stop(): void;
    getStatus(): {
        hasSchema: boolean;
        isPaused: boolean;
        error: string | null;
    };
}
