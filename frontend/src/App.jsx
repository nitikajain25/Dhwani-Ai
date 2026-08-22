import React, { useState, useEffect } from 'react';
import DhawaniAI from './DhawaniAI';
import { ExpandableTabsDemo } from './components/expandable-tabs-demo';
import NotFound from './components/NotFound';

function App() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  useEffect(() => {
    const handleLocationChange = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', handleLocationChange);
    return () => window.removeEventListener('popstate', handleLocationChange);
  }, []);

  const isHome = currentPath === '/' || currentPath === '/index.html';

  return (
    <>
      {isHome ? (
        <>
          <ExpandableTabsDemo />
          <DhawaniAI />
        </>
      ) : (
        <NotFound />
      )}
    </>
  );
}

export default App;
