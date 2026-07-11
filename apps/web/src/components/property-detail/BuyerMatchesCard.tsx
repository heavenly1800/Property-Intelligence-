import type { Buyer } from "../../services/buyerService";

type Props = {
  buyers: Buyer[];
};

export default function BuyerMatchesCard({
  buyers,
}: Props) {
  return (
    <section className="rounded-lg border bg-white p-6 shadow-sm">
      <h2 className="mb-6 text-xl font-semibold">
        Buyer Matches
      </h2>

      {buyers.length === 0 ? (
        <p className="text-gray-500">
          Click "Find Buyers" to search for matching investors.
        </p>
      ) : (
        <div className="space-y-4">
          {buyers.map((buyer) => (
            <div
              key={buyer.buyer_name}
              className="rounded border p-4"
            >
              <h3 className="font-semibold">
                {buyer.buyer_name}
              </h3>

              <p>
                Purchases: {buyer.purchase_count}
              </p>

              <p>
                Confidence: {buyer.confidence}%
              </p>

              <ul className="mt-2 list-disc pl-5 text-sm">
                {buyer.reasons.map((reason) => (
                  <li key={reason}>{reason}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}