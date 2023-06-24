import React, {useState} from 'react';
import '../DatabaseModellingStyle.css';
import DropdownList from "react-widgets/DropdownList";
import "react-widgets/styles.css";
import ConverterLogic from "./ConverterLogic"

const ConverterUI = () => {

    const {handleChange, clearData, sendData, setValue, message, updated, errorText} = ConverterLogic();

    return (

        <div style={{backgroundColor: '#222222', height: '100vh'}}>

            <div style={{backgroundColor: '#222222', flexDirection: 'row', flex: 1, display: 'flex'}}>
                <div style={{flex: 0.4, paddingTop: '10px'}}>
                    <textarea name="sqltext" value={message} placeholder="SQL-Input" onChange={handleChange} style={{width: "500px", height: "250px", fontSize: 14}}/>
                </div>


                <div style={{flex: 0.2, paddingTop: '50px'}}>
                    <button onClick={sendData} style={{height: "40px", width: "100px", backgroundColor:'#7df76f', fontSize: 14}}>Convert</button>

                    <button onClick={clearData} style={{height: "40px", width: "100px", backgroundColor:'#fc444a', fontSize: 14}}>Clear</button>

                    <DropdownList name="languagelist" onChange={value => setValue(value)} placeholder="Select language" data={["Cypher"]} style={{paddingTop: '20px'}}/>
                </div>


                <div style={{flex: 0.4, paddingTop: '10px'}}>
                    <textarea name="nosqltext" value={updated} placeholder="NoSQL-Output" style={{width: "500px", height: "250px", fontSize: 14}}/>
                </div>

            </div>
            
            <div>
                <span readOnly={true} style={{color: 'white', whiteSpace: 'pre-wrap'}}><b>Error Messages:</b>{errorText}</span>
            </div>

            
        </div>

    );
};
export default ConverterUI;
