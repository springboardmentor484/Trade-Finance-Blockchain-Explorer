export default function ActionButtons({ actions, onAction }) {
  return (
    <div className="flex gap-3 flex-wrap">
      {actions.map((action) => (
        <button
          key={action}
          className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white"
          onClick={() => onAction(action)}
        >
          {action}
        </button>
      ))}
    </div>
  );
}
