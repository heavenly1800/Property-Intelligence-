import type { BuyerMatch } from "../../services/buyerService";

type Props = {
  buyers: BuyerMatch[];
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

              {buyer.recommendation && (
                <p className="font-medium text-blue-600">
                  {buyer.recommendation}
                </p>
              )}

              {(buyer.strengths?.length ?? 0) > 0 && (
                <>
                  <h4 className="mt-2 font-medium">
                    Strengths
                  </h4>

                  <ul>
                    {buyer.strengths!.map((strength) => (
                      <li key={strength}>
                        {strength}
                      </li>
                    ))}
                  </ul>
                </>
              )}

              {(buyer.concerns?.length ?? 0) > 0 && (
                <>
                  <h4 className="mt-2 font-medium">
                    Concerns
                  </h4>

                  <ul>
                    {buyer.concerns!.map((concern) => (
                      <li key={concern}>
                        {concern}
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
