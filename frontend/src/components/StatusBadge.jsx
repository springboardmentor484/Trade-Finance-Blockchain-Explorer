export default function StatusBadge({ status }) {
  const color =
    status === "ISSUED"
      ? "bg-blue-500"
      : status === "ACCEPTED"
        ? "bg-green-500"
        : status === "SHIPPED"
          ? "bg-yellow-500"
          : status === "RECEIVED"
            ? "bg-purple-500"
            : status === "PAID"
              ? "bg-teal-500"
              : status === "VERIFIED"
                ? "bg-indigo-500"
                : "bg-gray-500";

  return (
    <span className={`text-white px-3 py-1 rounded-full ${color}`}>
      {status}
    </span>
  );
}
