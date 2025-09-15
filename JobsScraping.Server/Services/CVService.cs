using JobsScraping.Server.Data;
using JobsScraping.Server.Models;

namespace JobsScraping.Server.Services
{
    public class CVService : ICVService
    {
        private readonly ApplicationDbContext _context;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly IJobsService _jobService;

        public CVService(
            ApplicationDbContext context,
            IHttpContextAccessor httpContextAccessor,
            IJobsService jobService)
        {
            _context = context;
            _httpContextAccessor = httpContextAccessor;
            _jobService = jobService;
        }

        public Task<List<JobMatch>> FindMatchingJobsAsync()
        {
            throw new NotImplementedException();
        }

        public Task<CV> GetCVByUserIdAsync(string userId)
        {
            throw new NotImplementedException();
        }

        public async Task<List<string>> GetCVsAsync()
        {
            // This method should retrieve CVs from a database or other storage.
            // For now, it returns an empty list.
            return new List<string>();
        }

        public Task<CV> UpdateCVAsync(CV cv)
        {
            throw new NotImplementedException();
        }
    }
}
