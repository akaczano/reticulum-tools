import client from './client';

export const fetchStatus = async () => {
    const result = await client.get('/status')
    return result.data;
}

export const fetchInterfaces = async () => {
    const result = await client.get('/interfaces');
    return result.data;
}

export const fetchPaths = async () => {
    const result = await client.get('/paths');
    return result.data;
}

