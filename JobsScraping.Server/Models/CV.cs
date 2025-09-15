namespace JobsScraping.Server.Models
{
    public class CV
    {
        public int Id { get; set; }
        public string? Summary { get; set; }
        public List<Skill>? Skills { get; set; }
        public List<WorkExperience>? WorkExperiences { get; set; }
        public List<Education>? Educations { get; set; }
        public List<string>? Certifications { get; set; }
        public List<string>? Languages { get; set; }
        public string? OcrText { get; set; }
        public string? CVSource { get; set; }
        public DateTime CreatedDate { get; set; }
        public string? OriginalFileName { get; set; }
        public string? CVUrl { get; set; }
        // FK
        public int UserId { get; set; }
        public User? User { get; set; }
    }
}
