import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Spinner, Form, Stack, Row, Col, Button } from "react-bootstrap";

import { fetchMessages, fetchContacts, sendMessage } from "../api/messages";

import "./Messages.css"
import { fetchStatus } from "../api/status";

function Messages() {

    const [selectedTab, setTab] = useState(0);
    const [input, setInput] = useState("");
    const [sendError, setSendError] = useState("");


    const queryClient = useQueryClient();
    const statusQuery = useQuery({ queryKey: ['status'], queryFn: fetchStatus })
    const contactsQuery = useQuery({ queryKey: ['contacts'], queryFn: fetchContacts });

    const query = useQuery({ queryKey: ["messages"], queryFn: fetchMessages });
    const sendMutation = useMutation({
        mutationFn: sendMessage,
        onSuccess: () => {            
            queryClient.invalidateQueries({ queryKey: ["messages"]})
            setInput("");
            setSendError("");
        },
        onError: (error) => {            
            setSendError(error.message);
        }
    })



    const displayTabs = () => {
        return (
            <Stack direction="horizontal">
                {contactsQuery.data.map((c, idx) => {return (
                    <span className={"message-tab" + (idx === selectedTab ? " selected" : " unselected")} onClick={() => setTab(idx)}>
                        {c.name}
                    </span>
                )})}
            </Stack>
        )
    }

    const displayMessage = (user, msg) => {

        const outgoing = user.hash === msg.source;
        const timestamp = outgoing ? msg.time_sent : msg.time_received
        const className = outgoing ? "message-entry outgoing" : "message-entry incoming"        

        return (
            <div >
                <Stack className={className} >
                    <span className="message-time">
                        {timestamp}
                    </span> <br />
                    <span className="message-text">
                        {msg.text}
                    </span>  
                    <span className="message-source">
                        
                    </span>  
                </Stack>
            </div>
        )
    }

    const displayMessages = (user, contact, messages) => {

        if (messages.length < 1) {
            return (
                <div className="message-body">
                    <p>No messages from {contact.name}</p>
                </div>
            )
        }

        return (
            <div className="message-body">
                <Stack direction="vertical" gap={1}>
                    {messages.map(msg => displayMessage(user, msg))}
                </Stack>
            </div>
        )
    }

    const displayInput = (contact) => {

        const buttonContent = sendMutation.isPending ? 
            <Spinner animation="border" /> : "Send";

        const message = {
            hash: contact.hash,
            message: input
        }

        const feedback = sendError ? 
            <p className="send-error">{sendError}</p>
            : null;

        return (            
            <Row>
                <Form.Group as={Col} md={9}>                    
                    <Form.Control
                        type="text"
                        placeholder={`message ${contact.name}`}
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && input.length > 0 ? sendMutation.mutate(message) : {}}
                        />
                    {feedback}
                </Form.Group>  
                <Col>
                    <Button variant="primary" onClick={() => sendMutation.mutate(message)} disabled={input.length < 1}>
                        {buttonContent}
                    </Button>
                </Col>                                 
            </Row>
        )

    }

    const getContent = () => {

        if (query.isPending || contactsQuery.isPending) {
            return <Spinner animation="border" />
        }
        else if (query.error || !query.data || contactsQuery.error || !contactsQuery.data) {
            return <p style={{ color: 'red'}}>{query.error?.message || contactsQuery.error?.message || "There was a problem" }</p>
        }

        const user = statusQuery.data;
        const contact = contactsQuery.data[selectedTab];                        
        const messages = query.data.filter(m => m.destination === contact.hash || m.source === contact.hash)

        return (
            <Stack direction="vertical" gap={2}>
                {displayTabs()}
                {displayMessages(user, contact, messages)}
                {displayInput(contact)}
            </Stack>
        )
    }


    return (
        <div>
            <h3>Messages</h3> 
            <hr />           
            { getContent() }
        </div>
    )
}
export default Messages;