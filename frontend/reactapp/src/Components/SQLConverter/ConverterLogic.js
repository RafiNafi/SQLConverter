import React, {useState} from 'react';
import '../DatabaseModellingStyle.css';
import axios from "axios";
import "react-widgets/styles.css";

const ConverterLogic = () => {

    const urlSql = "http://localhost:5000/convert"

    const sendData = () => {

        setErrors("");
        setUpdated("");
    
        //prepare dto
        let dto = { query: message, 
                    language: value};
    
        //generate sql query
        generateNoSql(dto)
    }
    
    const clearData = () => {
        setMessage("");
        setUpdated("");
        setErrors("");
    }
    
    const handleChange = (event) => {
        setMessage(event.target.value);
    };
    
    function generateNoSql(dto){
    
        const seriousCodes = ["PRS", "RF01", "RF04", "AL04", "CV03", "CV07","LT06", "RF02", "RF03", "RF05", "ST07", "AM07"];

        console.log("data send: "+ dto.query+" language: "+dto.language)
    
        axios.post(urlSql, dto).
            then((response) => {
                console.log("response " + response.data)
    
                if(Array.isArray(response.data)){
    
                    let errorString = ["\n"]
                    let heavyErrors = false
    
                    for(let i=0;i<response.data[1].length;i++) {
                        console.log(response.data[1][i].description)
    
                        let errorDescription = response.data[1][i].description
                        let errorCode = response.data[1][i].code
                        let errorPos = response.data[1][i].line_pos
                        let errorLine = response.data[1][i].line_no
    
                        if(seriousCodes.includes(errorCode)) {
                            heavyErrors = true
                            errorDescription = "Error - Line: " + errorLine + " - Position: " + errorPos + " - Description: " + errorDescription
                        }
                        else {
                            errorDescription = "Warning - Line: " + errorLine + " - Position: " + errorPos + " - Description: " + errorDescription
                        }


                        errorString.push(
                            <span style={seriousCodes.includes(errorCode) ? { color: 'red' } : { color: 'yellow' }}>
                                {"\n" + errorDescription}
                            </span>
                          )
                        
                    }
    
                    setErrors(errorString)
    
                    if(!heavyErrors) {
                        setUpdated(response.data[0]);   
                    }
    
    
                }
            }).
            catch(error => {
                console.log(error)
                });
    }
    
    
    const [message, setMessage] = useState('');
    const [updated, setUpdated] = useState(message);
    const [value, setValue] = useState('')
    const [errorText, setErrors] = useState('')
    
    return {
        handleChange, clearData, sendData, setValue, message, updated, errorText
    }

};
export default ConverterLogic;
