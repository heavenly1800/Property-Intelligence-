import Card from "./Card";

type Props = {
  title: string;
  value: string | number;
};

export default function MetricCard({
  title,
  value,
}: Props) {
  return (
    <Card>
      <h3>{title}</h3>

      <h1>{value}</h1>
    </Card>
  );
}