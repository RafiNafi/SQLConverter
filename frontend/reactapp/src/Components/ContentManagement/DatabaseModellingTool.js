import '../../App.css';
import React, {useState} from "react";
import {DiagramTypes} from "../../Services/DrawBoardModel/Diagram";
import ErManager from '../ErModel/ErManager';
import ContentManager from "./ContentManager";
import RelationalManager from "../RelationalModel/RelationalManager";
import Converter from "../SQLConverter/Converter";

/**
 * Effective root of the database modelling application, renders the content manager
 * Here additional meta information and hooks can be provided to the Er and relational diagrams
 */
function DatabaseModellingTool() {

    const [diagramType, setDiagramType] = useState(DiagramTypes.erDiagram)

    function changeToErDiagram(){
        if(diagramType === DiagramTypes.erDiagram) return;
        setDiagramType(DiagramTypes.erDiagram);
    }

    function changeToRelationalDiagram(){
        if(diagramType === DiagramTypes.relationalDiagram) return;
        setDiagramType(DiagramTypes.relationalDiagram);
    }

    function changeToConverter(){
        if(diagramType === DiagramTypes.converter) return;
        setDiagramType(DiagramTypes.converter);
    }

    const projectVersion = 1.0;
    const projectName = "notNamed";

    const metaInformation = {
        projectVersion: projectVersion,
        projectName: projectName,
    }

    return (
        <React.StrictMode>
        <div className="App">
            <ContentManager metaInformation={metaInformation}
                            diagramType={diagramType}
                            changeToErDiagram={changeToErDiagram}
                            changeToRelationalDiagram={changeToRelationalDiagram}
                            changeToConverter={changeToConverter}>

        {(() => {
        switch(diagramType) {
            case DiagramTypes.erDiagram:
                return <ErManager/>;
            case DiagramTypes.relationalDiagram:
                return <RelationalManager/>;
            case DiagramTypes.converter:
                return <Converter/>;
            default:
                return null
        }
        })()}

            </ContentManager>
        </div>
        </React.StrictMode>
    )
}

export default DatabaseModellingTool;
