import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Spinner, Form, Stack, Row, Col, Button } from "react-bootstrap";

import { fetchMessages, fetchContacts } from "../api/messages";

import "./Messages.css"
import { fetchStatus } from "../api/status";

function Messages() {

    const [selectedTab, setTab] = useState(0);
    const statusQuery = useQuery({ queryKey: ['status'], queryFn: fetchStatus })
    const contactsQuery = useQuery({ queryKey: ['contacts'], queryFn: fetchContacts });

    const query = useQuery({ queryKey: ["messages"], queryFn: fetchMessages });

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

            </div>
        )
    }

    const displayInput = (contact) => {

        return (            
            <Form.Group as={Row}>
                <Col md={9}>
                    <Form.Control type="text" placeholder={`message ${contact.name}`} />
                </Col>
                <Col>
                    <Button variant="primary">Send</Button>
                </Col>            
            </Form.Group>            
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
        const messages = query.data.filter(m => m.source === user.hash || m.source === contact.hash)

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
            { getContent() }
        </div>
    )
}
export default Messages;