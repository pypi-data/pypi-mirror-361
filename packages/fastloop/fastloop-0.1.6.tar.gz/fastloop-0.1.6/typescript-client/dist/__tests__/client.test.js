"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const client_1 = require("../client");
describe('LoopClient', () => {
    let client;
    beforeEach(() => {
        client = new client_1.LoopClient();
    });
    test('should create a new client instance', () => {
        expect(client).toBeInstanceOf(client_1.LoopClient);
    });
    test('should configure loop with withLoop', () => {
        const options = {
            url: 'http://localhost:8111/pr-review',
            eventCallback: jest.fn(),
            loopId: 'test-loop'
        };
        const result = client.withLoop(options);
        expect(result).toBe(client);
    });
    test('should throw error when sending without configuration', async () => {
        await expect(client.send('test', {})).rejects.toThrow('Loop not configured');
    });
    test('should throw error when sending without connection', async () => {
        client.withLoop({
            url: 'http://localhost:8111/pr-review',
            eventCallback: jest.fn()
        });
        await expect(client.send('test', {})).rejects.toThrow('Loop not connected');
    });
    test('should handle pause and resume', () => {
        client.pause();
        expect(client.getStatus().isPaused).toBe(true);
        client.resume();
        expect(client.getStatus().isPaused).toBe(false);
    });
});
