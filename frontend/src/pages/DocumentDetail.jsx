import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";

export default function DocumentDetail() {
    const { id } = useParams();
    const [doc, setDoc] = useState(null);
    const [hashResult, setHashResult] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem("accessToken");

        api.get(`/document?id=${id}`, {
            headers : {
                Authorization: `Bearer ${token}`
            }
        })
        .then(res => setDoc(res.data))
        .catch(() => alert("Access Denied"));
    }, [id]);

    if (!doc) return <div>loading...</div>;

    const role = localStorage.getItem("role");
    const status = doc.document.status;
    const docType = doc.document.doc_type;

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

    const verifyHash = () => {
        const token = localStorage.getItem("accessToken");

        api.get(`/verify-hash?document_id=${id}`,
            { headers: 
                {
                Authorization: `Bearer ${token}`
                }
            }
        )
        .then(res => setHashResult(res.data))
        .catch(() => alert("Hash verification failed"));
    };



    return (
        <div>
            <h2>Document: {doc.document.doc_number}</h2>
            <p>Status: {doc.document.status}</p>

            <div>
                
                {/* SELLER */}
                {role === "seller" && docType === "PO" && status === "CREATED" && (
                <button className="mt-2 px-3 py-1 bg-orange-500 text-white rounded hover:bg-orange-700" 
                        onClick={() => performAction("ISSUE_BOL")}>
                        Issue BOL
                </button>
                )}

                {role === "seller" && status === "ISSUE_BOL" && (
                <button className="mt-2 px-3 py-1 bg-orange-500 text-white rounded hover:bg-orange-700"
                        onClick={() => performAction("SHIP")}>
                        Ship
                </button>
                )}

                {/* BUYER */}
                {role === "buyer" && status === "SHIP" && (
                <button className="mt-2 px-3 py-1 bg-orange-500 text-white rounded hover:bg-orange-700"
                        onClick={() => performAction("RECEIVE")}>
                    Receive
                </button>
                )}

                {/* AUDITOR */}
                {role === "auditor" && status !== "VERIFY" && (
                <button className="mt-2 px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-700"
                        onClick={() => performAction("VERIFY")}>
                    Verify
                </button>
                )}

                {role === "bank" && status === "CREATED" && (
                <button className="mt-2 px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-700"
                        onClick={() => performAction("ISSUE_LOC")}>
                    Issue LOC
                </button>
                )}

                {role === "bank" && status === "RECEIVE" && (
                <button className="mt-2 px-3 py-1 bg-green-500 text-white rounded hover:bg-green-700"
                        onClick={() => performAction("PAY")}>
                    Pay
                </button>
                )}

            {/* 5 buyer ,seller 4, auditor 3 ,bank 6 */}
            </div>

<br />

            <a  href={`http://127.0.0.1:8000/file?file_url=${doc.document.file_url}`}
                target="_blank"
                rel="noreferrer"
                className="mt-2 px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-700">Download File</a>
            <br />
            {/* <button onClick={verifyHash}
                    className="mt-4 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                Verify File Integrity
            </button> */}

            <button
                    onClick={verifyHash}
                    disabled={hashResult?.is_valid}
                    className={`mt-4 px-4 py-2 text-white rounded ${
                        hashResult?.is_valid
                        ? "bg-gray-400 cursor-not-allowed"
                        : "bg-green-600 hover:bg-green-700"
                    }`}
                    >
                    Verify File Integrity
            </button>

            {
                hashResult && (
                    <div className="mt-4 p-3 rounded border">
                        {hashResult.is_valid ? (
                        <p className="text-green-700 font-semibold">
                            ✅ File integrity verified. Hash matches.
                        </p>
                        ) : (
                        <p className="text-red-700 font-semibold">
                            ❌ File integrity compromised.
                        </p>
                        )}
                    </div>
                )
            }



            {/* <h3>Ledger Timeline</h3>
            <ul>
                {doc.ledger.map((entry, index) => (
                    <li key={index}>
                        {entry.action} by user {entry.actor_id} at {entry.created_at}
                    </li>
                ))}
            </ul> */}
                <h3 className="text-xl font-semibold mt-6 mb-3">Ledger Timeline</h3>

                {/* <div className="space-y-3">
                {doc.ledger.map((entry, index) => (
                    <div
                    key={index}
                    className="border-l-4 border-blue-600 bg-gray-50 p-3 rounded"
                    >
                    <p className="font-medium">{entry.action}</p>
                    <p className="text-sm text-gray-600">
                        Performed by User {entry.actor_id}
                    </p>
                    <p className="text-xs text-gray-500">
                        {new Date(entry.created_at).toLocaleString()}
                    </p>
                    </div>
                ))}
                </div> */}

                <div className="space-y-3">
                    {doc.ledger.map((entry, index) => (
                        <div
                        key={index}
                        className="border-l-4 border-blue-600 bg-gray-50 p-3 rounded"
                        >
                        <p className="font-medium">Action: {entry.action}</p>
                        <p className="text-sm text-gray-700">
                            Actor: {entry.actor_name} ({entry.actor_role})
                        </p>
                        <p className="text-sm text-gray-600">
                            Organization: {entry.actor_org}
                        </p>
                        <p className="text-xs text-gray-500">
                            {new Date(entry.created_at).toLocaleString()}
                        </p>
                        </div>
                    ))}
                </div>


        </div>
    );
}

