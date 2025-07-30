"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.useLoop = useLoop;
const react_1 = require("react");
const client_1 = require("./client");
function useLoop(options) {
    const [error, setError] = (0, react_1.useState)(null);
    const [eventTypes, setEventTypes] = (0, react_1.useState)({});
    const clientRef = (0, react_1.useRef)(null);
    const hasSchemaRef = (0, react_1.useRef)(false);
    const loopIdRef = (0, react_1.useRef)(options.loopId);
    const isSendingRef = (0, react_1.useRef)(false);
    const { url, eventCallback, loopId } = options;
    // Initialize client
    (0, react_1.useEffect)(() => {
        if (!clientRef.current) {
            clientRef.current = new client_1.LoopClient();
        }
        const client = clientRef.current;
        // Configure the loop
        client.withLoop({
            url,
            eventCallback,
            loopId: loopIdRef.current ?? undefined,
        });
        // Fetch event types
        if (!hasSchemaRef.current) {
            hasSchemaRef.current = true;
            client
                .setup()
                .then((eventTypes) => {
                setEventTypes(eventTypes);
            })
                .catch((err) => {
                setError(err instanceof Error ? err.message : "Failed to connect");
                hasSchemaRef.current = false;
            });
        }
        // Cleanup on unmount
        return () => {
            if (client) {
            }
        };
    }, [url, loopId]);
    // Open an SSE connection to event stream once we have a valid `loopId`.
    (0, react_1.useEffect)(() => {
        if (!loopIdRef.current || !eventCallback)
            return;
        // Extract base URL (protocol + host)
        let baseUrl;
        try {
            const { protocol, host } = new URL(url);
            baseUrl = `${protocol}//${host}`;
        }
        catch {
            baseUrl = url.split("/").slice(0, 3).join("/");
        }
        const sseUrl = `${baseUrl}/events/${loopIdRef.current}/sse`;
        const eventSource = new EventSource(sseUrl);
        eventSource.onmessage = (event) => {
            try {
                const parsed = JSON.parse(event.data);
                eventCallback(parsed);
            }
            catch {
                // Do nothing for invalid JSON
            }
        };
        eventSource.onerror = (err) => {
            console.error("SSE connection error:", err);
            eventSource.close();
        };
        return () => eventSource.close();
    }, [url, eventCallback, loopIdRef.current]);
    // Send function
    const send = (0, react_1.useCallback)(async (type, data) => {
        if (!clientRef.current) {
            return {
                success: false,
                error: "Client not initialized",
            };
        }
        // If no loopId yet, prevent concurrent sends
        if (!loopIdRef.current) {
            if (isSendingRef.current) {
                return {
                    success: false,
                    error: "Initial send already in progress",
                };
            }
            isSendingRef.current = true;
        }
        // Ensure client uses the latest loopId
        if (loopIdRef.current) {
            clientRef.current.withLoop({
                url,
                eventCallback,
                loopId: loopIdRef.current,
            });
        }
        try {
            const response = await clientRef.current.send(type, data);
            // Set loopId if it's the first successful send
            if (response.success && response.data?.loop_id && !loopIdRef.current) {
                loopIdRef.current = response.data.loop_id;
                clientRef.current.withLoop({
                    url,
                    eventCallback,
                    loopId: loopIdRef.current,
                });
            }
            return response;
        }
        catch (err) {
            const errorMessage = err instanceof Error ? err.message : "Unknown error";
            setError(errorMessage);
            return {
                success: false,
                error: errorMessage,
            };
        }
        finally {
            // Always reset sending state after initial send completes
            if (!loopIdRef.current) {
                isSendingRef.current = false;
            }
        }
    }, [url, eventCallback]);
    // Get event types
    const getEventTypes = (0, react_1.useCallback)(async () => {
        if (!clientRef.current)
            throw new Error("Client not initialized");
        try {
            const eventTypes = await clientRef.current.getEventTypes();
            setEventTypes(eventTypes);
            return eventTypes;
        }
        catch (err) {
            const errorMessage = err instanceof Error ? err.message : "Unknown error";
            setError(errorMessage);
            throw err;
        }
    }, []);
    // Stop function
    const stop = (0, react_1.useCallback)(() => {
        if (clientRef.current) {
            clientRef.current.stop();
        }
    }, []);
    // Pause function
    const pause = (0, react_1.useCallback)(() => {
        if (clientRef.current) {
            clientRef.current.pause();
        }
    }, []);
    return {
        send,
        getEventTypes,
        eventTypes,
        stop,
        pause,
        error,
        loopId: loopIdRef.current,
    };
}
