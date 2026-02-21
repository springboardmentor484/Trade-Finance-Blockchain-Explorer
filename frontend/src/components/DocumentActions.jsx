export default function DocumentActions({ actions, onAction }) {
  if (!actions || actions.length === 0) {
    return (
      <p className="text-sm text-gray-500 italic">
        No actions available
      </p>
    );
  }

  return (
    <div className="flex gap-3 mt-4">
      {actions.map((action) => (
        <button
          key={action}
          onClick={() => onAction(action)}
          className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition"
        >
          {action.replace("_", " ").toUpperCase()}
        </button>
      ))}
    </div>
  );
}
