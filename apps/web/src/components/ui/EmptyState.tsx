type Props = {
  message: string;
};

export default function EmptyState({
  message,
}: Props) {
  return (
    <div
      style={{
        padding: 40,
        textAlign: "center",
        color: "#777",
      }}
    >
      {message}
    </div>
  );
}