#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include <sys/types.h>
#include <pwd.h>
#include <grp.h>
#include <sys/stat.h>

int
main(int argc, char *argv[])
{

	struct stat sb;
	struct passwd *pwuser;
	struct group *grpnam;

	if (argc < 2)
	{
		fprintf(stderr, "Usage: %s: file ...\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	for (int i = 1; i < argc; i++)
	{
		if (-1 == stat(argv[i], &sb))
		{
			perror("stat()");
			exit(EXIT_FAILURE);
		}

		if (NULL == (pwuser = getpwuid(sb.st_uid)))
		{
			perror("getpwuid()");
			exit(EXIT_FAILURE);
		}

		if (NULL == (grpnam = getgrgid(sb.st_gid)))
		{
			perror("getgrgid()");
			exit(EXIT_FAILURE);
		}

		printf("%s:\n", argv[i]);
		printf("\tinode: %u\n", sb.st_ino);
		printf("\towner: %u (%s)\n", sb.st_uid, pwuser->pw_name);
		printf("\tgroup: %u (%s)\n", sb.st_gid, grpnam->gr_name);
		printf("\tst_mode: %u (%s)\n", sb.st_mode);
		printf("\tmode: %u (%s)\n", sb.st_mode-(S_IRWXU | S_IRWXG | S_IRWXO));
		printf("\tperms: %o\n", sb.st_mode & (S_IRWXU | S_IRWXG | S_IRWXO));
		printf("\tlinks: %d\n", sb.st_nlink);
		printf("\tsize: %ld\n", sb.st_size);
		printf("\tatime: %s", ctime(&sb.st_atim.tv_sec));
		printf("\tmtime: %s", ctime(&sb.st_mtim.tv_sec));
		printf("\tctime: %s", ctime(&sb.st_ctim.tv_sec));

		printf("\n");
	}

	return 0;
}
