type Props = {
  title: string;
  subtitle?: string;
};

export default function PageHeader({
  title,
  subtitle,
}: Props) {
  return (
    <div style={{ marginBottom: 30 }}>
      <h1>{title}</h1>

      {subtitle && (
        <p
          style={{
            color: "#666",
            marginTop: -10,
          }}
        >
          {subtitle}
        </p>
      )}
    </div>
  );
}