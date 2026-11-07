import client from './client';

export const fetchContacts = async () => {
    const result = await client.get('/contacts');
    return result.data;
}

export const fetchMessages = async () => {
    const result = await client.get('/messages');
    return result.data;

}

export const sendMessage = async (message) => {
    try {
        const result = await client.post('/send', message);
        return result;
    } catch (error) {
        throw Error(error.response.data.message);
    }
    
}