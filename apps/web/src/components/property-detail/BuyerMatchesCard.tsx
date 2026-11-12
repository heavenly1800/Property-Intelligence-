import type { BuyerMatch, BuyerMatchResult } from "../../services/buyerService";
import type { BuyerDiscoveryStatus } from "../../services/workflowService";

type Props = {
  buyers: BuyerMatch[];
  result?: BuyerMatchResult | null;
  status?: BuyerDiscoveryStatus;
  error?: string | null;
};

export default function BuyerMatchesCard({
  buyers,
  result,
  status = "not_searched",
  error = null,
}: Props) {
  return (
    <section className="buyer-matches-card">
      <h2>Buyer Matches</h2>

      {status === "failed" && <p className="media-error" role="alert">{error ?? "Buyer discovery failed."}</p>}

      {buyers.length === 0 ? (
        <p className="empty-buyer-state">
          {status === "no_verified_buyers" || result?.status === "no_verified_buyers"
            ? "No verified buyers found."
            : status === "failed"
              ? "No buyer-search completion was recorded."
              : 'Not searched in this session. Prior buyer-search history is unavailable.'}
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

              {buyer.purchase_count !== null && <p>Verified purchases: {buyer.purchase_count}</p>}

              {buyer.confidence !== null && <p>Confidence: {buyer.confidence}%</p>}

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
