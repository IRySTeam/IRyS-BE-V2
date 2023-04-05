from pydantic import BaseModel, Field

# ==============================================================================
# Request Body-related Schemas.
# ==============================================================================


# ==============================================================================
# Response Body-related Schemas.
# ==============================================================================
class ElasticVersion(BaseModel):
	number: str = Field(..., description="Version number")
	build_flavor: str = Field(..., description="Build flavor")
	build_type: str = Field(..., description="Build type either docker or rpm/deb")
	build_hash: str = Field(..., description="Hash of the build")
	build_date: str = Field(..., description="Timestamp of the build")
	build_snapshot: bool = Field(..., description="Whether the build is a snapshot or not")
	lucene_version: str = Field(..., description="Version of Apache Lucene used")
	minimum_wire_compatibility_version: str = Field(
   ..., 
   description="Minimum wire version needed to communicate with this node"
  )
	minimum_index_compatibility_version: str = Field(
   ..., 
   description="Minimum index version"
  )

# Elasticsearch cluster information returned by the Elasticsearch client info() method.
class ElasticInfo(BaseModel):
	name: str = Field(..., description="Name of the deployment instance")
	cluster_name: str = Field(..., description="Name of the cluster")
	cluster_uuid: str = Field(..., description="Unique identifier for the cluster")
	version: ElasticVersion = Field(..., description="Version of the Elastic Stack")
	tagline: str = Field(..., description="Catch phrase for the Elastic Stack")
 
# ==============================================================================
# Path parameters-related Schemas.
# ==============================================================================
    
# ==============================================================================
# Query parameters-related Schemas.
# ==============================================================================
