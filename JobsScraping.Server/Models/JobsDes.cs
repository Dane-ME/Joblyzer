namespace JobsScraping.Server.Models
{
    public class JobsDes
    {
        public int Id { get; set; }
        public string? Title { get; set; }
        public string? Company { get; set; }
        public string? Location { get; set; }
        public string? Description { get; set; }
        public string? Url { get; set; }
        public DateTime PostedDate { get; set; }
        public string? JobType { get; set; }
        public string? Salary { get; set; }
        public string? ExperienceLevel { get; set; }
        public string? Industry { get; set; }
        public string? EmploymentType { get; set; }
        public string? RequiredSkills { get; set; }
        public string? Benefits { get; set; }
        public string? Source { get; set; }
        public string? RawContent { get; set; }
    }
}
