import tickersData from './tickers.json';

/**
 * Interface for ticker data
 */
interface TickerData {
  name: string;
  type: string;
  sector: string;
  industry: string;
  source: string;
}

/**
 * Interface for search result
 */
interface SearchResult {
  ticker: string;
  name: string;
  type: string;
  source: string;
  score: number;
}

/**
 * Tools for interacting with web services and external APIs
 */
export class WebTools {
  private tickers: Record<string, TickerData>;

  constructor() {
    this.tickers = tickersData as Record<string, TickerData>;
  }

  /**
   * Search for tickers matching the query string
   * @param args Configuration options
   * @param args.query Search string to match against ticker symbols or names
   * @param args.limit Maximum number of results to return (default: 5, max: 5)
   * @returns JSON string with list of matching tickers
   */
  async search_dataset(args: {
    query: string;
    limit?: number;
  }): Promise<string> {
    try {
      const { query, limit = 5 } = args;

      if (!query || query.trim() === '') {
        return JSON.stringify({
          error: 'Query parameter is required and cannot be empty'
        });
      }

      // Enforce maximum limit of 5
      const maxLimit = Math.min(limit, 5);

      // Prepare search choices with ticker symbols and names
      const choices: Array<{ ticker: string; searchText: string }> = [];

      for (const [ticker, data] of Object.entries(this.tickers)) {
        choices.push({
          ticker,
          searchText: `${ticker}: ${data.name}`
        });
      }

      // Perform fuzzy search using simple string matching
      const results = this.fuzzySearch(query, choices, maxLimit);

      // Format the results
      const matchedTickers: SearchResult[] = results.map(result => ({
        ticker: result.ticker,
        name: this.tickers[result.ticker].name,
        type: this.tickers[result.ticker].type,
        source: this.tickers[result.ticker].source,
        score: result.score
      }));

      return JSON.stringify(matchedTickers);
    } catch (error) {
      console.error('Error searching datasets:', error);
      return JSON.stringify({
        error: `Failed to search datasets: ${error instanceof Error ? error.message : String(error)}`
      });
    }
  }

  /**
   * Simple fuzzy search implementation
   * @param query Search query
   * @param choices Array of choices to search through
   * @param limit Maximum number of results
   * @returns Array of search results with scores
   */
  private fuzzySearch(
    query: string,
    choices: Array<{ ticker: string; searchText: string }>,
    limit: number
  ): Array<{ ticker: string; score: number }> {
    const queryLower = query.toLowerCase();
    const results: Array<{ ticker: string; score: number }> = [];

    for (const choice of choices) {
      const searchTextLower = choice.searchText.toLowerCase();
      const tickerLower = choice.ticker.toLowerCase();

      let score = 0;

      // Exact ticker match gets highest score
      if (tickerLower === queryLower) {
        score = 100;
      }
      // Ticker starts with query gets high score
      else if (tickerLower.startsWith(queryLower)) {
        score = 90;
      }
      // Ticker contains query gets medium score
      else if (tickerLower.includes(queryLower)) {
        score = 80;
      }
      // Name contains query gets lower score
      else if (searchTextLower.includes(queryLower)) {
        score = 70;
      }
      // Partial matches using simple substring matching
      else {
        // Calculate similarity based on common characters
        const commonChars = this.getCommonCharacters(
          queryLower,
          searchTextLower
        );
        if (commonChars > 0) {
          score = Math.min(60, (commonChars / queryLower.length) * 60);
        }
      }

      if (score > 0) {
        results.push({
          ticker: choice.ticker,
          score
        });
      }
    }

    // Sort by score (descending) and return top results
    return results.sort((a, b) => b.score - a.score).slice(0, limit);
  }

  /**
   * Count common characters between two strings
   * @param str1 First string
   * @param str2 Second string
   * @returns Number of common characters
   */
  private getCommonCharacters(str1: string, str2: string): number {
    let common = 0;
    const chars1 = str1.split('');
    const chars2 = str2.split('');

    for (const char of chars1) {
      const index = chars2.indexOf(char);
      if (index !== -1) {
        common++;
        chars2.splice(index, 1); // Remove matched character
      }
    }

    return common;
  }
}
