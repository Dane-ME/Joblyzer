using JobsScraping.Server.Models;
using Microsoft.AspNetCore.Mvc;

namespace JobsScraping.Server.Controllers
{
    [Route("api/[controller]")]
    public class JobsScrapyController : ControllerBase
    {
        private readonly IJobsService _jobsService;
        private readonly ILogger<JobsScrapyController> _logger;

        public JobsScrapyController(IJobsService jobService, ILogger<JobsScrapyController> logger)
        {
            _jobsService = jobService;
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<List<JobsDes>>> GetJobs()
        {
            // This method should call the service to get job postings.
            // For now, it returns an empty list.
            return Ok(new List<JobsDes>());
        }
    }
}
