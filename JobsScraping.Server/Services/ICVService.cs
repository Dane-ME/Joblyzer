using JobsScraping.Server.Models;

namespace JobsScraping.Server.Services
{
    public interface ICVService
    {
        /// <summary>
        /// Gets the CVs from the database.
        /// </summary>
        /// <returns>A list of CVs.</returns>
        Task<List<string>> GetCVsAsync();
        Task<CV> GetCVByUserIdAsync(string userId);
        Task<CV> UpdateCVAsync(CV cv);
        Task<List<JobMatch>> FindMatchingJobsAsync(); // Tìm jobs phù hợp với CV
    }
}
