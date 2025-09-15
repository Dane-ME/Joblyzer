namespace JobsScraping.Server.Models
{
    public class JobMatch
    {
        public int Id { get; set; }
        public JobsDes? Job { get; set; }
        public string? MatchedSkills { get; set; }
        public decimal? MatchScore { get; set; }
        public DateTime CreatedDate { get; set; }
    }
}
