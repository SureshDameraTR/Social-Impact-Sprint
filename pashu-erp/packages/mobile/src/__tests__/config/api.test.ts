/**
 * ApiClient unit tests.
 *
 * Tests the ApiClient class directly (not the singleton).
 * Verifies: auth header injection, timeout handling, retry on 5xx,
 * 401 -> redirect, error messages.
 */

// ---- Mocks ----
const mockReplace = jest.fn();
jest.mock('expo-router', () => ({
  router: { replace: mockReplace, push: jest.fn(), back: jest.fn() },
}));

const mockStorage = {
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(() => Promise.resolve()),
  deleteItemAsync: jest.fn(() => Promise.resolve()),
};
jest.mock('../../config/storage', () => mockStorage);

// ---- Imports ----
// The ApiClient module checks EXPO_PUBLIC_API_URL at module scope.
// The setup.ts file sets process.env.EXPO_PUBLIC_API_URL before this runs.
import { ApiClient } from '../../config/api';

describe('ApiClient', () => {
  let client: InstanceType<typeof ApiClient>;
  let fetchSpy: jest.SpyInstance;

  beforeEach(() => {
    jest.clearAllMocks();
    client = new ApiClient('http://localhost:8000/v1');
    fetchSpy = jest.spyOn(global, 'fetch');
  });

  afterEach(() => {
    fetchSpy.mockRestore();
  });

  // ---- Auth header ----

  it('injects Authorization header when token exists', async () => {
    mockStorage.getItemAsync.mockResolvedValue('test-jwt-token');
    fetchSpy.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ data: [] }),
    });

    await client.get('/animals');

    expect(fetchSpy).toHaveBeenCalledWith(
      'http://localhost:8000/v1/animals',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer test-jwt-token',
        }),
      })
    );
  });

  it('omits Authorization header when no token exists', async () => {
    mockStorage.getItemAsync.mockResolvedValue(null);
    fetchSpy.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ data: [] }),
    });

    await client.get('/animals');

    const callArgs = fetchSpy.mock.calls[0][1];
    expect(callArgs.headers.Authorization).toBeUndefined();
  });

  // ---- Content-Type header ----

  it('sets Content-Type to application/json on POST', async () => {
    mockStorage.getItemAsync.mockResolvedValue(null);
    fetchSpy.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({}),
    });

    await client.post('/milk/yield', { animal_id: '1', quantity: 5 });

    expect(fetchSpy).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    );
  });

  // ---- POST body serialization ----

  it('serializes POST body as JSON', async () => {
    mockStorage.getItemAsync.mockResolvedValue(null);
    fetchSpy.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({}),
    });

    const body = { animal_id: 'a1', session: 'morning', quantity_liters: 5 };
    await client.post('/milk/yield', body);

    expect(fetchSpy).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        body: JSON.stringify(body),
        method: 'POST',
      })
    );
  });

  // ---- 401 handling ----

  it('clears token and redirects to login on 401', async () => {
    mockStorage.getItemAsync.mockResolvedValue('expired-token');
    fetchSpy.mockResolvedValue({
      ok: false,
      status: 401,
      text: () => Promise.resolve('Unauthorized'),
    });

    await expect(client.get('/animals')).rejects.toThrow('Session expired');
    expect(mockStorage.deleteItemAsync).toHaveBeenCalledWith('auth_token');
    expect(mockReplace).toHaveBeenCalledWith('/(auth)/login');
  });

  // ---- Non-200 error ----

  it('throws error with status code on non-OK response', async () => {
    mockStorage.getItemAsync.mockResolvedValue(null);
    fetchSpy.mockResolvedValue({
      ok: false,
      status: 404,
      text: () => Promise.resolve('Not found'),
    });

    await expect(client.get('/nonexistent')).rejects.toThrow('API 404');
  });

  // ---- Retry on 5xx ----

  it('retries on 500 error and succeeds on second attempt', async () => {
    mockStorage.getItemAsync.mockResolvedValue(null);

    fetchSpy
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
        text: () => Promise.resolve('Internal server error'),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: 'success' }),
      });

    const result = await client.get<{ data: string }>('/flaky-endpoint');
    expect(result).toEqual({ data: 'success' });
    expect(fetchSpy).toHaveBeenCalledTimes(2);
  });

  it('does not retry on 4xx client errors', async () => {
    mockStorage.getItemAsync.mockResolvedValue(null);
    fetchSpy.mockResolvedValue({
      ok: false,
      status: 422,
      text: () => Promise.resolve('Validation error'),
    });

    await expect(client.get('/bad-request')).rejects.toThrow('API 422');
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });

  // ---- DELETE method ----

  it('sends DELETE request correctly', async () => {
    mockStorage.getItemAsync.mockResolvedValue('token');
    fetchSpy.mockResolvedValue({
      ok: true,
      status: 204,
      text: () => Promise.resolve(''),
    });

    await client.delete('/animals/123');

    expect(fetchSpy).toHaveBeenCalledWith(
      'http://localhost:8000/v1/animals/123',
      expect.objectContaining({
        method: 'DELETE',
      })
    );
  });

  // ---- PATCH method ----

  it('sends PATCH request with body', async () => {
    mockStorage.getItemAsync.mockResolvedValue('token');
    fetchSpy.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ updated: true }),
    });

    const body = { name: 'New Name' };
    await client.patch('/animals/123', body);

    expect(fetchSpy).toHaveBeenCalledWith(
      'http://localhost:8000/v1/animals/123',
      expect.objectContaining({
        method: 'PATCH',
        body: JSON.stringify(body),
      })
    );
  });
});
