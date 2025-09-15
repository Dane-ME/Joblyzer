using Microsoft.EntityFrameworkCore;
using JobsScraping.Server.Models;

namespace JobsScraping.Server.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        // DbSets
        public DbSet<User> Users { get; set; }
        public DbSet<CV> CVs { get; set; }
        public DbSet<JobsDes> Jobs { get; set; }
        public DbSet<Skill> Skills { get; set; }
        public DbSet<WorkExperience> WorkExperiences { get; set; }
        public DbSet<Education> Educations { get; set; }
        public DbSet<JobMatch> JobMatches { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // Configure entities
            ConfigureUser(modelBuilder);
            ConfigureCV(modelBuilder);
            ConfigureJob(modelBuilder);
            ConfigureSkill(modelBuilder);
            ConfigureWorkExperience(modelBuilder);
            ConfigureEducation(modelBuilder);
            ConfigureJobMatch(modelBuilder);

            // Configure custom indexes
            ConfigureCustomIndexes(modelBuilder);
        }

        private void ConfigureUser(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<User>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                
                entity.Property(e => e.Name).HasMaxLength(100);
                entity.Property(e => e.Email).IsRequired().HasMaxLength(100);
                entity.Property(e => e.Password).HasMaxLength(255);
                entity.Property(e => e.PhoneNumber).HasMaxLength(20);
                entity.Property(e => e.Address).HasMaxLength(500);
                entity.Property(e => e.DateOfBirth).HasColumnType("datetime2");
                entity.Property(e => e.ProfilePictureUrl).HasMaxLength(500);
                entity.Property(e => e.CreatedAt).HasColumnType("datetime2").HasDefaultValueSql("GETUTCDATE()");
                entity.Property(e => e.UpdatedAt).HasColumnType("datetime2").HasDefaultValueSql("GETUTCDATE()");
                entity.Property(e => e.Role).HasMaxLength(50);

                // Unique constraints
                entity.HasIndex(e => e.Email).IsUnique();
                entity.HasIndex(e => e.Name).HasFilter("[Name] IS NOT NULL");
            });
        }

        private void ConfigureCV(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<CV>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                
                entity.Property(e => e.Summary).HasMaxLength(2000);
                entity.Property(e => e.OcrText).HasMaxLength(4000);
                entity.Property(e => e.CVSource).HasMaxLength(100);
                entity.Property(e => e.CreatedDate).HasColumnType("datetime2").HasDefaultValueSql("GETUTCDATE()");
                entity.Property(e => e.OriginalFileName).HasMaxLength(255);
                entity.Property(e => e.CVUrl).HasMaxLength(500);
                
                // Handle List<string> properties as JSON or separate table
                entity.Property(e => e.Certifications).HasConversion(
                    v => string.Join(',', v ?? new List<string>()),
                    v => v.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList()
                );
                
                entity.Property(e => e.Languages).HasConversion(
                    v => string.Join(',', v ?? new List<string>()),
                    v => v.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList()
                );

                // Relationship với User
                entity.HasOne(e => e.User)
                      .WithMany(u => u.CV)
                      .HasForeignKey(e => e.UserId)
                      .OnDelete(DeleteBehavior.Cascade);

                // Indexes
                entity.HasIndex(e => e.UserId);
            });
        }

        private void ConfigureJob(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<JobsDes>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                
                entity.Property(e => e.Title).IsRequired().HasMaxLength(200);
                entity.Property(e => e.Company).IsRequired().HasMaxLength(200);
                entity.Property(e => e.Location).HasMaxLength(200);
                entity.Property(e => e.Description).HasMaxLength(5000);
                entity.Property(e => e.Url).HasMaxLength(500);
                entity.Property(e => e.PostedDate).HasColumnType("datetime2");
                entity.Property(e => e.JobType).HasMaxLength(100);
                entity.Property(e => e.Salary).HasMaxLength(100);
                entity.Property(e => e.ExperienceLevel).HasMaxLength(100);
                entity.Property(e => e.Industry).HasMaxLength(100);
                entity.Property(e => e.EmploymentType).HasMaxLength(100);
                entity.Property(e => e.RequiredSkills).HasMaxLength(1000);
                entity.Property(e => e.Benefits).HasMaxLength(1000);
                entity.Property(e => e.Source).HasMaxLength(100);

                // Indexes cho search performance
                entity.HasIndex(e => e.Title);
                entity.HasIndex(e => e.Company);
                entity.HasIndex(e => e.Location);
                entity.HasIndex(e => e.PostedDate);
                entity.HasIndex(e => e.Industry);
                entity.HasIndex(e => e.JobType);
                entity.HasIndex(e => e.ExperienceLevel);
                
                // Composite indexes
                entity.HasIndex(e => new { e.Title, e.Location, e.PostedDate })
                      .HasDatabaseName("IX_Jobs_Title_Location_PostedDate");
                      
                entity.HasIndex(e => new { e.Company, e.Industry })
                      .HasDatabaseName("IX_Jobs_Company_Industry");
            });
        }

        private void ConfigureSkill(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<Skill>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                
                entity.Property(e => e.Name).IsRequired().HasMaxLength(100);
                entity.Property(e => e.Description).HasMaxLength(500);

                // Many-to-Many relationship với CVs
                entity.HasMany(s => s.CVs)
                      .WithMany(c => c.Skills)
                      .UsingEntity<Dictionary<string, object>>(
                          "CVSkill",
                          j => j.HasOne<CV>()
                                .WithMany()
                                .HasForeignKey("CVId")
                                .OnDelete(DeleteBehavior.Cascade),
                          j => j.HasOne<Skill>()
                                .WithMany()
                                .HasForeignKey("SkillId")
                                .OnDelete(DeleteBehavior.Cascade)
                      );

                // Indexes
                entity.HasIndex(e => e.Name).IsUnique();
                entity.HasIndex(e => e.Description).HasFilter("[Description] IS NOT NULL");
            });
        }

        private void ConfigureWorkExperience(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<WorkExperience>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                
                entity.Property(e => e.JobTitle).HasMaxLength(200);
                entity.Property(e => e.CompanyName).HasMaxLength(200);
                entity.Property(e => e.Location).HasMaxLength(200);
                entity.Property(e => e.StartDate).HasColumnType("datetime2");
                entity.Property(e => e.EndDate).HasColumnType("datetime2");
                entity.Property(e => e.Description).HasMaxLength(2000);

                // Relationship với CV
                entity.HasOne(e => e.CV)
                      .WithMany(c => c.WorkExperiences)
                      .HasForeignKey(e => e.CVId)
                      .OnDelete(DeleteBehavior.Cascade);

                // Indexes
                entity.HasIndex(e => e.CVId);
                entity.HasIndex(e => e.JobTitle);
                entity.HasIndex(e => e.CompanyName);
                entity.HasIndex(e => e.StartDate);
                entity.HasIndex(e => e.EndDate);
                
                // Composite index
                entity.HasIndex(e => new { e.CVId, e.StartDate, e.EndDate })
                      .HasDatabaseName("IX_WorkExperience_CVId_DateRange");
            });
        }

        private void ConfigureEducation(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<Education>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                
                entity.Property(e => e.Degree).HasMaxLength(200);
                entity.Property(e => e.Institution).HasMaxLength(200);
                entity.Property(e => e.Location).HasMaxLength(200);
                entity.Property(e => e.StartDate).HasColumnType("datetime2");
                entity.Property(e => e.EndDate).HasColumnType("datetime2");
                entity.Property(e => e.Description).HasMaxLength(2000);

                // Relationship với CV
                entity.HasOne(e => e.CV)
                      .WithMany(c => c.Educations)
                      .HasForeignKey(e => e.CVId)
                      .OnDelete(DeleteBehavior.Cascade);

                // Indexes
                entity.HasIndex(e => e.CVId);
                entity.HasIndex(e => e.Degree);
                entity.HasIndex(e => e.Institution);
                entity.HasIndex(e => e.StartDate);
                entity.HasIndex(e => e.EndDate);
                
                // Composite index
                entity.HasIndex(e => new { e.CVId, e.Degree, e.Institution })
                      .HasDatabaseName("IX_Education_CVId_Degree_Institution");
            });
        }

        private void ConfigureJobMatch(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<JobMatch>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Id).ValueGeneratedOnAdd();
                
                entity.Property(e => e.MatchedSkills).HasMaxLength(1000);
                entity.Property(e => e.MatchScore).HasColumnType("decimal(5, 2)");
                entity.Property(e => e.CreatedDate).HasColumnType("datetime2").HasDefaultValueSql("GETUTCDATE()");

                // Relationship với Job (nếu cần)
                // entity.HasOne(e => e.Job).WithMany().HasForeignKey("JobId");
            });
        }

        private void ConfigureCustomIndexes(ModelBuilder modelBuilder)
        {
            // Full-text search index cho job descriptions (SQL Server specific)
            modelBuilder.Entity<JobsDes>()
                .HasIndex(j => j.Description)
                .HasDatabaseName("IX_Jobs_Description_FullText");

            // Index cho user search
            modelBuilder.Entity<User>()
                .HasIndex(u => new { u.Name, u.Email })
                .HasDatabaseName("IX_Users_Name_Email")
                .HasFilter("[Name] IS NOT NULL");

            // Index cho CV search
            modelBuilder.Entity<CV>()
                .HasIndex(c => new { c.UserId })
                .HasDatabaseName("IX_CVs_UserId_Name")
                .HasFilter("[Name] IS NOT NULL");

            // Index cho skill search
            modelBuilder.Entity<Skill>()
                .HasIndex(s => new { s.Name, s.Description })
                .HasDatabaseName("IX_Skills_Name_Description")
                .HasFilter("[Description] IS NOT NULL");
        }
    }
}