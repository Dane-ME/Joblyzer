namespace JobsScraping.Server.Models
{
    public class WorkExperience
    {
        public int Id { get; set; }
        public string? JobTitle { get; set; }
        public string? CompanyName { get; set; }
        public string? Location { get; set; }
        public DateTime StartDate { get; set; }
        public DateTime EndDate { get; set; }
        public string? Description { get; set; }
        // FK
        public int CVId { get; set; }
        public CV CV { get; set; } = null!;
    }
}
