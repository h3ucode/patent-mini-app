import React, { createContext, useContext, useState } from 'react';

const SelectionContext = createContext();

export const SelectionProvider = ({ children }) => {
  const [selectedPatent, setSelectedPatent] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(null);

  return (
    <SelectionContext.Provider 
      value={{ 
        selectedPatent, 
        setSelectedPatent, 
        selectedCompany, 
        setSelectedCompany 
      }}
    >
      {children}
    </SelectionContext.Provider>
  );
};

export const useSelection = () => useContext(SelectionContext); 