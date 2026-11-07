import { fetchContacts } from '../api/messages';
import { useQuery } from '@tanstack/react-query';
import { Spinner, Table } from 'react-bootstrap';

function Contacts() {

    const query = useQuery({ queryKey: ['contacts'], queryFn: fetchContacts });

    const getContent = () => {
        if (query.isPending) {
            return <Spinner animation='border' />
        }
        else if (query.error || !query.data) {
            return <p style={{ color: 'red'}}>{query.error?.message || "There was a problem" }</p>
        }
        else {
            console.log(query.data);
            return (
                <Table bordered hover striped>
                    <thead>
                        <tr>                            
                            <th>Name</th>
                            <th>Hash</th>
                        </tr>                        
                    </thead>
                    <tbody>
                        {query.data.map( contact => { return (
                            <tr key={`contact_table_row_${contact.hash}`}>                                
                                <td>{contact.name}</td>
                                <td>{contact.hash}</td>
                            </tr>
                        )})}
                    </tbody>
                </Table>
            )
        }
    }

    return (
        <div>
            <h3>Contacts</h3>
            <hr />
            {getContent()}
        </div>
    );
}

export default Contacts;