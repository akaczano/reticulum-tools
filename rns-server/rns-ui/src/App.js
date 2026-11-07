import './App.css';
import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { Button, Row, Col, ListGroup, Stack } from 'react-bootstrap' 
import { GrConnect, GrMailOption } from "react-icons/gr";
import { SlPeople } from "react-icons/sl";
import { GiPathDistance } from "react-icons/gi";

import Interfaces from './components/Interfaces';
import Paths from './components/Paths';
import Messages from './components/Messages';
import Contacts from './components/Contacts';

import './App.css';

const tabs = [
  { description: "Interfaces", icon: <GrConnect />, component: <Interfaces /> },
  { description: "Paths", icon: <GiPathDistance />, component: <Paths /> },
  { description: "Contacts", icon: <SlPeople />, component: <Contacts /> },
  { description: "Messages", icon: <GrMailOption />, component: <Messages /> }
];


function App() {
  const queryClient = new QueryClient();
  const [tab, setTab] = useState(0);

  const currentTab = tabs[tab];
  
  return (
    <div style={{}}>
        <div className="header">
          <h2>RNS Messenger</h2>
        </div>
        <div className="divider horizontal"></div>
        <Stack direction='horizontal'>
          <div className="sidebar">
            { tabs.map( (t, idx) => { return (
              <p className={tab === idx ? "side-link selected" : "side-link"} onClick={() => setTab(idx)}>
                {t.icon}
                {t.description}
              </p>
            )})}
          </div>
          <div className="divider vertical"></div>
          <div className="content">
            { currentTab.component }
          </div>

        </Stack>
        
    </div>      

  );
}

export default App;
