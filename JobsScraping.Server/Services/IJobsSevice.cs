using JobsScraping.Server.Models;

public interface IJobsService
{
    /// <summary>
    /// Scrapes jobs from the specified URL.
    /// </summary>
    /// <param name="url">The URL to scrape jobs from.</param>
    /// <returns>A list of scraped job postings.</returns>
    Task<List<JobsDes>> ScrapeJobsAsync(string url);
    /// <summary>
    /// Gets the job postings from the database.
    /// </summary>
    /// <returns>A list of job postings.</returns>
    Task<List<JobsDes>> GetJobPostingsAsync();
}