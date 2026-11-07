import { fetchInterfaces } from '../api/status';
import { useQuery } from '@tanstack/react-query';
import { Spinner } from 'react-bootstrap';

function Interfaces() {

    const query = useQuery({ queryKey: ['interfaces'], queryFn: fetchInterfaces })

    const getContent = () => {
    
        if (query.isPending) {
            return <Spinner animation='border' size='lg' />
        }
        else if (query.error || !query.data) {
            return <p color="red">{query.error?.message || "There was a problem"}</p>
        }
        console.log(query.data);
        return <p>There are {query.data.interfaces.length} interfaces connected.</p>
    }
    return (
        <div>            
            <h3> Interfaces </h3>
            <hr />
            { getContent() }
        </div>
    )
} 

export default Interfaces;