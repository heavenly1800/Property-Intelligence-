import type { Buyer } from "../../services/buyerService";

type Props = {
  buyers: Buyer[];
};

export default function BuyerMatchesCard({
  buyers,
}: Props) {
  return (
    <section className="buyer-matches-card">
      <h2>Buyer Matches</h2>

      {buyers.length === 0 ? (
        <p className="empty-buyer-state">
          Click "Find Buyers" to search for matching investors.
        </p>
      ) : (
        <div className="buyer-list">
          {buyers.map((buyer) => (
            <div
              key={buyer.buyer_name}
              className="buyer-match"
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

              <ul>
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
