import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";

export default function DocumentDetail() {
    const { id } = useParams();
    const [doc, setDoc] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem("accessToken");

        api.get(`/document?id=${id}`,{
            headers : {
                Authorization: `Bearer ${token}`
            }
        })
        .then(res => setDoc(res.data))
        .catch(() => alert("Access Denied"));
    }, [id]);

    if (!doc) return <div>loading...</div>;


    const performAction = (action) => {
        const token = localStorage.getItem("accessToken");

        api.post("/action", null, {
            params: {
                doc_id: id,
                action: action
            },
            headers: {
                Authorization: `Bearer ${token}`
            }
        })
        .then(() => window.location.reload())
        .catch(() => alert("Action not allowed"));
    };



    return (
        <div>
            <h2>Document: {doc.document.doc_number}</h2>
            <p>Status: {doc.document.status}</p>

            <button onClick={() => performAction("SHIP")}>ship</button>
            <button onClick={() => performAction("RECEIVE")}>receive</button>
            <button onClick={() => performAction("VERIFY")}>verify</button>



            <a href={`http://127.0.0.1:8000/file?file_url=${doc.document.file_url}`}
                target="_blank"
                rel="noreferrer">Download File</a>

            <h3>Ledger Timeline</h3>
            <ul>
                {doc.ledger.map((entry, index) => (
                    <li key={index}>
                        {entry.action} by user {entry.actor_id} at {entry.created_at}
                    </li>
                ))}
            </ul>
        </div>
    );
}

