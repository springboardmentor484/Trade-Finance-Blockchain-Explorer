import StatusBadge from "./StatusBadge";

export default function DocumentCard({ document, onSelect }) {
  return (
    <div
      className="border rounded p-4 shadow hover:shadow-lg cursor-pointer"
      onClick={() => onSelect(document.id)}
    >
      <div className="flex justify-between items-center">
        <h3 className="font-semibold">{document.doc_number}</h3>
        <StatusBadge status={document.status} />
      </div>

      <p className="text-sm text-gray-500 mt-2">
        Type: {document.doc_type}
      </p>
    </div>
  );
}
