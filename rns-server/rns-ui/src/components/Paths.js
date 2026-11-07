import { fetchPaths } from "../api/status";
import { useQuery } from "@tanstack/react-query";
import { Spinner, Table} from 'react-bootstrap';

function Paths() {
    const query =  useQuery({ queryKey: ['paths'], queryFn: fetchPaths});
    const getContent = () => {
        if (query.isPending) {
            return <Spinner animation="border" /> 
        }
        else if (query.error || !query.data) {
            return <p style={{ color: 'red'}}>{query.error?.message || "There was a problem"}</p>
        }               
        return (
            <Table bordered striped hover>
                <thead>
                    <tr>
                        <th>Hash</th>
                        <th>Interface</th>                        
                        <th>Hops</th>
                        <th>Via</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    {query.data.map(path => { console.log(path.timestamp); return (
                        <tr>
                            <td>{path.hash}</td>
                            <td>{path.interface}</td>
                            <td>{path.hops}</td>                            
                            <td>{path.via}</td>
                            <td>{new Date(path.timestamp * 1000).toLocaleString()}</td>
                        </tr>
                    ) })}
                </tbody>
            </Table>
        )

    }    
    return (
        <div>
            <h3>Path Table</h3>
            <hr />
            {getContent()}
        </div>
    )
}

export default Paths;