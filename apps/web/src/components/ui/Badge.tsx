type Props = {
  text: string;
};

export default function Badge({ text }: Props) {
  return (
    <span
      style={{
        background: "#e8f5e9",
        color: "#2e7d32",
        padding: "4px 10px",
        borderRadius: 20,
        fontSize: 12,
        fontWeight: 600,
      }}
    >
      {text}
    </span>
  );
}