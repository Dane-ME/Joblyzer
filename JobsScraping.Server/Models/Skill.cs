namespace JobsScraping.Server.Models
{
    public class Skill
    {
        public int Id { get; set; }
        public string? Name { get; set; }
        public string? Description { get; set; }
        // Navigation property to link to CVs
        public List<CV>? CVs { get; set; }
        // Navigation property to link to JobsDes
        public List<JobsDes>? Jobs { get; set; }

        // Navigation property to link to WorkExperience
        public List<WorkExperience>? WorkExperiences { get; set; }

        // Navigation property to link to Education
        public List<Education>? Educations { get; set; }
    }
}
