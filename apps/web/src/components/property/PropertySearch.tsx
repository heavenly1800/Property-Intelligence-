type Props = {
  value: string;
  onChange: (value: string) => void;
};

export default function PropertySearch({
  value,
  onChange,
}: Props) {
  return (
    <input
      placeholder="Search properties..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
      style={{
        width: "100%",
        padding: 12,
        marginBottom: 20,
        borderRadius: 8,
        border: "1px solid #ccc",
      }}
    />
  );
}